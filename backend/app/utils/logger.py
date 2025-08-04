import structlog
import logging
import sys
from typing import Any, Dict
from datetime import datetime


def setup_logger(log_level: str = "INFO") -> structlog.BoundLogger:
    """Setup structured logger for the application."""
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


def log_aws_operation(operation: str, service: str, region: str, **kwargs) -> None:
    """Log AWS operation with structured data."""
    logger = structlog.get_logger()
    logger.info(
        "AWS operation executed",
        operation=operation,
        service=service,
        region=region,
        **kwargs
    )


def log_recommendation_implementation(
    check_id: str, 
    success: bool, 
    savings: float = None, 
    affected_resources: list = None
) -> None:
    """Log recommendation implementation with structured data."""
    logger = structlog.get_logger()
    logger.info(
        "Recommendation implementation",
        check_id=check_id,
        success=success,
        savings=savings,
        affected_resources=affected_resources or []
    )


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with structured data."""
    logger = structlog.get_logger()
    logger.error(
        "Application error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    )


# Global logger instance
logger = setup_logger() 