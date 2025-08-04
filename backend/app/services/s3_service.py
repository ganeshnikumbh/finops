import boto3
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError

from ..models import ImplementationResponse
from ..utils.logger import logger, log_aws_operation, log_error
from config import settings


class S3Service:
    """Service for S3-related automations."""
    
    def __init__(self):
        self.client = boto3.client('s3', region_name=settings.aws_region)
        self.logger = logger
    
    async def enable_versioning(self, dry_run: bool = False) -> ImplementationResponse:
        """Enable versioning on S3 buckets for data protection."""
        try:
            # Get all buckets
            buckets = await self._get_all_buckets()
            buckets_without_versioning = await self._identify_buckets_without_versioning(buckets)
            
            if not buckets_without_versioning:
                return ImplementationResponse(
                    success=True,
                    message="All buckets already have versioning enabled",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                return ImplementationResponse(
                    success=True,
                    message=f"Would enable versioning on {len(buckets_without_versioning)} buckets",
                    savings=0.0,  # Versioning doesn't save money, it's for protection
                    affected_resources=buckets_without_versioning,
                    dry_run=dry_run
                )
            
            # Enable versioning
            enabled_buckets = await self._enable_versioning_on_buckets(buckets_without_versioning)
            
            log_aws_operation(
                "enable_versioning",
                "s3",
                settings.aws_region,
                buckets_enabled=len(enabled_buckets)
            )
            
            return ImplementationResponse(
                success=True,
                message=f"Successfully enabled versioning on {len(enabled_buckets)} buckets",
                savings=0.0,
                affected_resources=enabled_buckets,
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "enable_versioning"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to enable versioning: {str(e)}",
                dry_run=dry_run
            )
    
    async def _get_all_buckets(self) -> List[str]:
        """Get all S3 buckets."""
        try:
            response = self.client.list_buckets()
            return [bucket['Name'] for bucket in response['Buckets']]
            
        except Exception as e:
            log_error(e, {"operation": "_get_all_buckets"})
            raise
    
    async def _identify_buckets_without_versioning(self, buckets: List[str]) -> List[str]:
        """Identify buckets without versioning enabled."""
        buckets_without_versioning = []
        
        for bucket_name in buckets:
            try:
                if not await self._has_versioning_enabled(bucket_name):
                    buckets_without_versioning.append(bucket_name)
            except Exception as e:
                log_error(e, {"bucket_name": bucket_name})
                continue
        
        return buckets_without_versioning
    
    async def _has_versioning_enabled(self, bucket_name: str) -> bool:
        """Check if versioning is enabled on a bucket."""
        try:
            response = self.client.get_bucket_versioning(Bucket=bucket_name)
            status = response.get('Status')
            return status == 'Enabled'
            
        except Exception as e:
            log_error(e, {"bucket_name": bucket_name})
            return False
    
    async def _enable_versioning_on_buckets(self, bucket_names: List[str]) -> List[str]:
        """Enable versioning on the specified buckets."""
        enabled_buckets = []
        
        for bucket_name in bucket_names:
            try:
                self.client.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                
                enabled_buckets.append(bucket_name)
                
                log_aws_operation(
                    "enable_bucket_versioning",
                    "s3",
                    settings.aws_region,
                    bucket_name=bucket_name
                )
                
            except Exception as e:
                log_error(e, {"bucket_name": bucket_name})
                continue
        
        return enabled_buckets
    
    async def enable_logging(self, dry_run: bool = False) -> ImplementationResponse:
        """Enable logging on S3 buckets for security and compliance."""
        try:
            # Get all buckets
            buckets = await self._get_all_buckets()
            buckets_without_logging = await self._identify_buckets_without_logging(buckets)
            
            if not buckets_without_logging:
                return ImplementationResponse(
                    success=True,
                    message="All buckets already have logging enabled",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                return ImplementationResponse(
                    success=True,
                    message=f"Would enable logging on {len(buckets_without_logging)} buckets",
                    savings=0.0,  # Logging doesn't save money, it's for security
                    affected_resources=buckets_without_logging,
                    dry_run=dry_run
                )
            
            # Enable logging
            enabled_buckets = await self._enable_logging_on_buckets(buckets_without_logging)
            
            log_aws_operation(
                "enable_logging",
                "s3",
                settings.aws_region,
                buckets_enabled=len(enabled_buckets)
            )
            
            return ImplementationResponse(
                success=True,
                message=f"Successfully enabled logging on {len(enabled_buckets)} buckets",
                savings=0.0,
                affected_resources=enabled_buckets,
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "enable_logging"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to enable logging: {str(e)}",
                dry_run=dry_run
            )
    
    async def _identify_buckets_without_logging(self, buckets: List[str]) -> List[str]:
        """Identify buckets without logging enabled."""
        buckets_without_logging = []
        
        for bucket_name in buckets:
            try:
                if not await self._has_logging_enabled(bucket_name):
                    buckets_without_logging.append(bucket_name)
            except Exception as e:
                log_error(e, {"bucket_name": bucket_name})
                continue
        
        return buckets_without_logging
    
    async def _has_logging_enabled(self, bucket_name: str) -> bool:
        """Check if logging is enabled on a bucket."""
        try:
            response = self.client.get_bucket_logging(Bucket=bucket_name)
            return 'LoggingEnabled' in response
            
        except Exception as e:
            log_error(e, {"bucket_name": bucket_name})
            return False
    
    async def _enable_logging_on_buckets(self, bucket_names: List[str]) -> List[str]:
        """Enable logging on the specified buckets."""
        enabled_buckets = []
        
        for bucket_name in bucket_names:
            try:
                # Create a logging bucket name
                logging_bucket = f"{bucket_name}-logs"
                
                # Try to create logging bucket if it doesn't exist
                try:
                    self.client.create_bucket(
                        Bucket=logging_bucket,
                        CreateBucketConfiguration={
                            'LocationConstraint': settings.aws_region
                        }
                    )
                except ClientError as e:
                    if e.response['Error']['Code'] != 'BucketAlreadyExists':
                        raise
                
                # Enable logging
                self.client.put_bucket_logging(
                    Bucket=bucket_name,
                    BucketLoggingStatus={
                        'LoggingEnabled': {
                            'TargetBucket': logging_bucket,
                            'TargetPrefix': f"{bucket_name}/"
                        }
                    }
                )
                
                enabled_buckets.append(bucket_name)
                
                log_aws_operation(
                    "enable_bucket_logging",
                    "s3",
                    settings.aws_region,
                    bucket_name=bucket_name,
                    logging_bucket=logging_bucket
                )
                
            except Exception as e:
                log_error(e, {"bucket_name": bucket_name})
                continue
        
        return enabled_buckets
    
    async def optimize_storage_classes(self, dry_run: bool = False) -> ImplementationResponse:
        """Optimize S3 storage classes for cost savings."""
        try:
            # Get all buckets
            buckets = await self._get_all_buckets()
            optimizable_objects = await self._identify_optimizable_objects(buckets)
            
            if not optimizable_objects:
                return ImplementationResponse(
                    success=True,
                    message="No objects found for storage class optimization",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                savings = await self._calculate_storage_optimization_savings(optimizable_objects)
                return ImplementationResponse(
                    success=True,
                    message=f"Would optimize storage class for {len(optimizable_objects)} objects",
                    savings=savings,
                    affected_resources=list(set([obj['bucket'] for obj in optimizable_objects])),
                    dry_run=dry_run
                )
            
            # In a real implementation, you would change storage classes
            savings = await self._calculate_storage_optimization_savings(optimizable_objects)
            
            return ImplementationResponse(
                success=True,
                message=f"Identified {len(optimizable_objects)} objects for storage class optimization",
                savings=savings,
                affected_resources=list(set([obj['bucket'] for obj in optimizable_objects])),
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "optimize_storage_classes"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to optimize storage classes: {str(e)}",
                dry_run=dry_run
            )
    
    async def _identify_optimizable_objects(self, buckets: List[str]) -> List[Dict[str, Any]]:
        """Identify objects that could be optimized."""
        optimizable_objects = []
        
        for bucket_name in buckets:
            try:
                # List objects in bucket
                paginator = self.client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=bucket_name)
                
                for page in pages:
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            # Check if object is older than 30 days and in STANDARD storage class
                            if obj['StorageClass'] == 'STANDARD':
                                # In a real implementation, you'd check object age
                                # For now, we'll assume some objects are optimizable
                                optimizable_objects.append({
                                    'bucket': bucket_name,
                                    'key': obj['Key'],
                                    'size': obj['Size'],
                                    'storage_class': obj['StorageClass']
                                })
                                
            except Exception as e:
                log_error(e, {"bucket_name": bucket_name})
                continue
        
        return optimizable_objects
    
    async def _calculate_storage_optimization_savings(self, objects: List[Dict[str, Any]]) -> float:
        """Calculate savings from storage class optimization."""
        total_savings = 0.0
        
        for obj in objects:
            size_gb = obj['size'] / (1024 * 1024 * 1024)  # Convert bytes to GB
            
            # Simplified pricing (in a real implementation, you'd use AWS Pricing API)
            # STANDARD: $0.023 per GB, IA: $0.0125 per GB, Glacier: $0.004 per GB
            standard_cost = size_gb * 0.023
            ia_cost = size_gb * 0.0125
            glacier_cost = size_gb * 0.004
            
            # Calculate potential savings
            savings = standard_cost - ia_cost  # Move to IA
            total_savings += savings
        
        return total_savings
    
    async def remove_public_access(self, dry_run: bool = False) -> ImplementationResponse:
        """Remove public access from S3 buckets for security."""
        try:
            # Get all buckets
            buckets = await self._get_all_buckets()
            public_buckets = await self._identify_public_buckets(buckets)
            
            if not public_buckets:
                return ImplementationResponse(
                    success=True,
                    message="No buckets with public access found",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                return ImplementationResponse(
                    success=True,
                    message=f"Would remove public access from {len(public_buckets)} buckets",
                    savings=0.0,  # Security improvement, not cost savings
                    affected_resources=public_buckets,
                    dry_run=dry_run
                )
            
            # Remove public access
            secured_buckets = await self._remove_public_access_from_buckets(public_buckets)
            
            log_aws_operation(
                "remove_public_access",
                "s3",
                settings.aws_region,
                buckets_secured=len(secured_buckets)
            )
            
            return ImplementationResponse(
                success=True,
                message=f"Successfully removed public access from {len(secured_buckets)} buckets",
                savings=0.0,
                affected_resources=secured_buckets,
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "remove_public_access"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to remove public access: {str(e)}",
                dry_run=dry_run
            )
    
    async def _identify_public_buckets(self, buckets: List[str]) -> List[str]:
        """Identify buckets with public access."""
        public_buckets = []
        
        for bucket_name in buckets:
            try:
                if await self._has_public_access(bucket_name):
                    public_buckets.append(bucket_name)
            except Exception as e:
                log_error(e, {"bucket_name": bucket_name})
                continue
        
        return public_buckets
    
    async def _has_public_access(self, bucket_name: str) -> bool:
        """Check if a bucket has public access."""
        try:
            # Check bucket ACL
            acl = self.client.get_bucket_acl(Bucket=bucket_name)
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                if grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    return True
            
            # Check bucket policy
            try:
                policy = self.client.get_bucket_policy(Bucket=bucket_name)
                # In a real implementation, you'd parse the policy to check for public access
                return True
            except ClientError:
                # No bucket policy
                pass
            
            return False
            
        except Exception as e:
            log_error(e, {"bucket_name": bucket_name})
            return False
    
    async def _remove_public_access_from_buckets(self, bucket_names: List[str]) -> List[str]:
        """Remove public access from the specified buckets."""
        secured_buckets = []
        
        for bucket_name in bucket_names:
            try:
                # Set bucket ACL to private
                self.client.put_bucket_acl(
                    Bucket=bucket_name,
                    ACL='private'
                )
                
                secured_buckets.append(bucket_name)
                
                log_aws_operation(
                    "remove_bucket_public_access",
                    "s3",
                    settings.aws_region,
                    bucket_name=bucket_name
                )
                
            except Exception as e:
                log_error(e, {"bucket_name": bucket_name})
                continue
        
        return secured_buckets 