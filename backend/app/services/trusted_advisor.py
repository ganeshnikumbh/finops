import boto3
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

from ..models import RecommendationBase, CheckStatus, CheckCategory
from ..utils.logger import logger, log_aws_operation, log_error
from config import settings


class TrustedAdvisorService:
    """Service for interacting with AWS Trusted Advisor."""
    
    def __init__(self):
        self.client = boto3.client('support', region_name=settings.aws_region)
        self.logger = logger
    
    async def get_recommendations(self) -> List[RecommendationBase]:
        """Fetch Trusted Advisor recommendations asynchronously."""
        try:
            # Get available checks
            checks = await self._get_available_checks()
            recommendations = []
            
            for check in checks:
                try:
                    recommendation = await self._process_check(check)
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    log_error(e, {"check_id": check.get('checkId')})
                    continue
            
            return recommendations
            
        except Exception as e:
            log_error(e, {"operation": "get_recommendations"})
            raise
    
    async def _get_available_checks(self) -> List[Dict[str, Any]]:
        """Get available Trusted Advisor checks."""
        try:
            response = self.client.describe_trusted_advisor_checks(
                language='en'
            )
            
            log_aws_operation(
                "describe_trusted_advisor_checks",
                "support",
                settings.aws_region
            )
            
            return response.get('checks', [])
            
        except Exception as e:
            log_error(e, {"operation": "_get_available_checks"})
            raise
    
    async def _process_check(self, check: Dict[str, Any]) -> Optional[RecommendationBase]:
        """Process a single Trusted Advisor check."""
        try:
            check_id = check.get('id')
            check_result = await self._get_check_result(check_id)
            
            if not check_result:
                return None
            
            # Map check to recommendation
            recommendation = self._map_check_to_recommendation(check, check_result)
            return recommendation
            
        except Exception as e:
            log_error(e, {"check_id": check.get('id')})
            return None
    
    async def _get_check_result(self, check_id: str) -> Optional[Dict[str, Any]]:
        """Get the result for a specific check."""
        try:
            response = self.client.describe_trusted_advisor_check_result(
                checkId=check_id,
                language='en'
            )
            
            log_aws_operation(
                "describe_trusted_advisor_check_result",
                "support",
                settings.aws_region,
                check_id=check_id
            )
            
            return response.get('result', {})
            
        except Exception as e:
            log_error(e, {"check_id": check_id})
            return None
    
    def _map_check_to_recommendation(
        self, 
        check: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> RecommendationBase:
        """Map Trusted Advisor check to recommendation model."""
        
        # Map status
        status_mapping = {
            'ok': CheckStatus.OK,
            'warning': CheckStatus.WARNING,
            'error': CheckStatus.ERROR,
            'not_available': CheckStatus.NOT_AVAILABLE
        }
        
        status = status_mapping.get(
            result.get('status', 'not_available'),
            CheckStatus.NOT_AVAILABLE
        )
        
        # Map category
        category_mapping = {
            'cost_optimizing': CheckCategory.COST_OPTIMIZATION,
            'security': CheckCategory.SECURITY,
            'fault_tolerance': CheckCategory.FAULT_TOLERANCE,
            'performance': CheckCategory.PERFORMANCE
        }
        
        category = category_mapping.get(
            check.get('category', 'cost_optimizing'),
            CheckCategory.COST_OPTIMIZATION
        )
        
        # Determine if can be implemented
        can_implement = self._can_implement_check(check.get('id'), category)
        
        # Calculate estimated savings
        estimated_savings = self._calculate_estimated_savings(result)
        
        # Get affected resources
        affected_resources = self._get_affected_resources(result)
        
        return RecommendationBase(
            check_id=check.get('id'),
            category=category,
            title=check.get('name', 'Unknown Check'),
            description=check.get('description', 'No description available'),
            status=status,
            estimated_savings=estimated_savings,
            can_implement=can_implement,
            affected_resources=affected_resources,
            last_updated=datetime.now()
        )
    
    def _can_implement_check(self, check_id: str, category: CheckCategory) -> bool:
        """Determine if a check can be automatically implemented."""
        # Define checks that can be automated
        implementable_checks = {
            # Cost optimization checks
            'eBSgp2Check': True,  # EBS gp2 to gp3 migration
            'idleLoadBalancerCheck': True,  # Idle load balancers
            'unusedEBSVolumeCheck': True,  # Unused EBS volumes
            's3BucketVersioningCheck': True,  # S3 bucket versioning
            'rdsIdleDBInstanceCheck': True,  # Idle RDS instances
            
            # Security checks
            's3BucketLoggingCheck': True,  # S3 bucket logging
            's3BucketPublicReadCheck': True,  # S3 bucket public access
            
            # Performance checks
            'ec2InstanceCheck': True,  # EC2 instance optimization
        }
        
        return implementable_checks.get(check_id, False)
    
    def _calculate_estimated_savings(self, result: Dict[str, Any]) -> Optional[float]:
        """Calculate estimated savings from check result."""
        try:
            # This is a simplified calculation
            # In a real implementation, you would parse the detailed results
            flagged_resources = result.get('flaggedResources', [])
            
            if not flagged_resources:
                return 0.0
            
            # Estimate $50 per flagged resource (simplified)
            estimated_savings = len(flagged_resources) * 50.0
            
            return estimated_savings
            
        except Exception as e:
            log_error(e, {"operation": "_calculate_estimated_savings"})
            return None
    
    def _get_affected_resources(self, result: Dict[str, Any]) -> List[str]:
        """Extract affected resources from check result."""
        try:
            flagged_resources = result.get('flaggedResources', [])
            resources = []
            
            for resource in flagged_resources:
                resource_id = resource.get('metadata', [{}])[0].get('value')
                if resource_id:
                    resources.append(resource_id)
            
            return resources
            
        except Exception as e:
            log_error(e, {"operation": "_get_affected_resources"})
            return []
    
    async def test_connection(self) -> bool:
        """Test AWS connection and Trusted Advisor access."""
        try:
            # Try to describe checks to test connection
            self.client.describe_trusted_advisor_checks(language='en')
            return True
        except (ClientError, NoCredentialsError) as e:
            log_error(e, {"operation": "test_connection"})
            return False 