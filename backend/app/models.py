from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class CheckStatus(str, Enum):
    """Trusted Advisor check status enumeration."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    NOT_AVAILABLE = "not_available"


class CheckCategory(str, Enum):
    """Trusted Advisor check category enumeration."""
    COST_OPTIMIZATION = "cost_optimization"
    SECURITY = "security"
    FAULT_TOLERANCE = "fault_tolerance"
    PERFORMANCE = "performance"


class RecommendationBase(BaseModel):
    """Base model for recommendation data."""
    check_id: str = Field(..., description="Unique identifier for the check")
    category: CheckCategory = Field(..., description="Category of the check")
    title: str = Field(..., description="Title of the recommendation")
    description: str = Field(..., description="Detailed description of the recommendation")
    status: CheckStatus = Field(..., description="Current status of the check")
    estimated_savings: Optional[float] = Field(None, description="Estimated monthly savings in USD")
    can_implement: bool = Field(False, description="Whether this recommendation can be automatically implemented")
    affected_resources: Optional[List[str]] = Field(None, description="List of affected AWS resources")
    last_updated: Optional[datetime] = Field(None, description="Last time the check was updated")


class RecommendationResponse(BaseModel):
    """Response model for recommendations endpoint."""
    recommendations: List[RecommendationBase]
    total_count: int
    total_savings: float
    last_refresh: datetime


class ImplementationRequest(BaseModel):
    """Request model for implementing a recommendation."""
    dry_run: bool = Field(False, description="Whether to perform a dry run without making changes")
    force: bool = Field(False, description="Whether to force implementation without confirmation")


class ImplementationResponse(BaseModel):
    """Response model for implementation endpoint."""
    success: bool
    message: str
    savings: Optional[float] = Field(None, description="Actual savings achieved")
    affected_resources: List[str] = Field(default_factory=list)
    dry_run: bool = False
    implementation_time: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    aws_connection: bool 