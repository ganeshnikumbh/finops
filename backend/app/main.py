from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from .models import (
    RecommendationResponse, 
    ImplementationRequest, 
    ImplementationResponse,
    HealthCheckResponse,
    ErrorResponse
)
from .services.trusted_advisor import TrustedAdvisorService
from .services.ec2_service import EC2Service
from .services.ebs_service import EBSService
from .services.s3_service import S3Service
from .utils.logger import logger, log_error
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AWS FinOps Application for Trusted Advisor Recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
trusted_advisor_service = TrustedAdvisorService()
ec2_service = EC2Service()
ebs_service = EBSService()
s3_service = S3Service()


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with application information."""
    return {
        "message": "AWS FinOps Application",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Test AWS connection
        aws_connection = await trusted_advisor_service.test_connection()
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now(),
            aws_connection=aws_connection
        )
    except Exception as e:
        log_error(e, {"operation": "health_check"})
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            aws_connection=False
        )


@app.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations():
    """Get Trusted Advisor recommendations."""
    try:
        logger.info("Fetching Trusted Advisor recommendations")
        
        recommendations = await trusted_advisor_service.get_recommendations()
        
        # Calculate totals
        total_count = len(recommendations)
        total_savings = sum(rec.estimated_savings or 0 for rec in recommendations)
        
        return RecommendationResponse(
            recommendations=recommendations,
            total_count=total_count,
            total_savings=total_savings,
            last_refresh=datetime.now()
        )
        
    except Exception as e:
        log_error(e, {"operation": "get_recommendations"})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recommendations: {str(e)}"
        )


@app.post("/implement/{check_id}", response_model=ImplementationResponse)
async def implement_recommendation(
    check_id: str,
    request: ImplementationRequest,
    background_tasks: BackgroundTasks
):
    """Implement a Trusted Advisor recommendation."""
    try:
        logger.info(f"Implementing recommendation for check_id: {check_id}")
        
        # Map check_id to appropriate service and method
        implementation_result = await _execute_implementation(check_id, request.dry_run)
        
        # Log the implementation
        background_tasks.add_task(
            _log_implementation,
            check_id,
            implementation_result.success,
            implementation_result.savings,
            implementation_result.affected_resources
        )
        
        return implementation_result
        
    except Exception as e:
        log_error(e, {"operation": "implement_recommendation", "check_id": check_id})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to implement recommendation: {str(e)}"
        )


async def _execute_implementation(check_id: str, dry_run: bool) -> ImplementationResponse:
    """Execute the appropriate implementation based on check_id."""
    
    # Map check_id to implementation method
    implementation_map = {
        # EC2 checks
        'idleLoadBalancerCheck': lambda: ec2_service.stop_idle_instances(dry_run),
        'ec2InstanceCheck': lambda: ec2_service.optimize_instance_types(dry_run),
        
        # EBS checks
        'unusedEBSVolumeCheck': lambda: ebs_service.delete_unused_volumes(dry_run),
        'eBSgp2Check': lambda: ebs_service.migrate_gp2_to_gp3(dry_run),
        
        # S3 checks
        's3BucketVersioningCheck': lambda: s3_service.enable_versioning(dry_run),
        's3BucketLoggingCheck': lambda: s3_service.enable_logging(dry_run),
        's3BucketPublicReadCheck': lambda: s3_service.remove_public_access(dry_run),
        
        # Default implementations for common checks
        'idleEC2InstanceCheck': lambda: ec2_service.stop_idle_instances(dry_run),
        'unattachedEBSVolumeCheck': lambda: ebs_service.delete_unused_volumes(dry_run),
        's3StorageOptimizationCheck': lambda: s3_service.optimize_storage_classes(dry_run),
    }
    
    # Get the implementation function
    implementation_func = implementation_map.get(check_id)
    
    if not implementation_func:
        return ImplementationResponse(
            success=False,
            message=f"No implementation available for check_id: {check_id}",
            dry_run=dry_run
        )
    
    # Execute the implementation
    return await implementation_func()


async def _log_implementation(
    check_id: str,
    success: bool,
    savings: float,
    affected_resources: List[str]
):
    """Log implementation results."""
    logger.info(
        "Recommendation implementation completed",
        check_id=check_id,
        success=success,
        savings=savings,
        affected_resources_count=len(affected_resources)
    )


@app.get("/implementations/{check_id}/status")
async def get_implementation_status(check_id: str):
    """Get the status of a specific implementation."""
    try:
        # In a real implementation, you would store and retrieve implementation status
        # For now, we'll return a mock status
        return {
            "check_id": check_id,
            "status": "completed",
            "last_updated": datetime.now().isoformat(),
            "message": "Implementation completed successfully"
        }
    except Exception as e:
        log_error(e, {"operation": "get_implementation_status", "check_id": check_id})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get implementation status: {str(e)}"
        )


@app.get("/automations/available")
async def get_available_automations():
    """Get list of available automations."""
    return {
        "automations": [
            {
                "id": "stop_idle_instances",
                "name": "Stop Idle EC2 Instances",
                "description": "Stop idle EC2 instances to reduce costs",
                "service": "EC2",
                "estimated_savings": "Variable",
                "risk_level": "Low"
            },
            {
                "id": "delete_unused_volumes",
                "name": "Delete Unused EBS Volumes",
                "description": "Delete unattached EBS volumes to reduce costs",
                "service": "EBS",
                "estimated_savings": "Variable",
                "risk_level": "Medium"
            },
            {
                "id": "enable_versioning",
                "name": "Enable S3 Versioning",
                "description": "Enable versioning on S3 buckets for data protection",
                "service": "S3",
                "estimated_savings": "0 (Security improvement)",
                "risk_level": "Low"
            },
            {
                "id": "migrate_gp2_to_gp3",
                "name": "Migrate GP2 to GP3",
                "description": "Migrate GP2 volumes to GP3 for cost savings",
                "service": "EBS",
                "estimated_savings": "20% cost reduction",
                "risk_level": "Low"
            }
        ]
    }


@app.post("/automations/{automation_id}/execute")
async def execute_automation(
    automation_id: str,
    request: ImplementationRequest
):
    """Execute a specific automation."""
    try:
        # Map automation_id to service method
        automation_map = {
            "stop_idle_instances": lambda: ec2_service.stop_idle_instances(request.dry_run),
            "delete_unused_volumes": lambda: ebs_service.delete_unused_volumes(request.dry_run),
            "enable_versioning": lambda: s3_service.enable_versioning(request.dry_run),
            "migrate_gp2_to_gp3": lambda: ebs_service.migrate_gp2_to_gp3(request.dry_run),
            "optimize_instance_types": lambda: ec2_service.optimize_instance_types(request.dry_run),
            "enable_logging": lambda: s3_service.enable_logging(request.dry_run),
            "remove_public_access": lambda: s3_service.remove_public_access(request.dry_run),
        }
        
        automation_func = automation_map.get(automation_id)
        
        if not automation_func:
            raise HTTPException(
                status_code=404,
                detail=f"Automation {automation_id} not found"
            )
        
        result = await automation_func()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"operation": "execute_automation", "automation_id": automation_id})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute automation: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    log_error(exc, {"operation": "global_exception_handler"})
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.debug else None
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 