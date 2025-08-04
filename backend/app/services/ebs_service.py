import boto3
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

from ..models import ImplementationResponse
from ..utils.logger import logger, log_aws_operation, log_error
from config import settings


class EBSService:
    """Service for EBS-related automations."""
    
    def __init__(self):
        self.client = boto3.client('ec2', region_name=settings.aws_region)
        self.logger = logger
    
    async def delete_unused_volumes(self, dry_run: bool = False) -> ImplementationResponse:
        """Delete unused EBS volumes to reduce costs."""
        try:
            # Get all volumes
            volumes = await self._get_all_volumes()
            unused_volumes = await self._identify_unused_volumes(volumes)
            
            if not unused_volumes:
                return ImplementationResponse(
                    success=True,
                    message="No unused volumes found",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                savings = await self._calculate_volume_savings(unused_volumes)
                return ImplementationResponse(
                    success=True,
                    message=f"Would delete {len(unused_volumes)} unused volumes",
                    savings=savings,
                    affected_resources=[vol['VolumeId'] for vol in unused_volumes],
                    dry_run=dry_run
                )
            
            # Delete volumes
            deleted_volumes = await self._delete_volumes(unused_volumes)
            
            savings = await self._calculate_volume_savings(deleted_volumes)
            
            log_aws_operation(
                "delete_unused_volumes",
                "ec2",
                settings.aws_region,
                volumes_deleted=len(deleted_volumes),
                savings=savings
            )
            
            return ImplementationResponse(
                success=True,
                message=f"Successfully deleted {len(deleted_volumes)} unused volumes",
                savings=savings,
                affected_resources=[vol['VolumeId'] for vol in deleted_volumes],
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "delete_unused_volumes"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to delete unused volumes: {str(e)}",
                dry_run=dry_run
            )
    
    async def _get_all_volumes(self) -> List[Dict[str, Any]]:
        """Get all EBS volumes."""
        try:
            response = self.client.describe_volumes()
            return response['Volumes']
            
        except Exception as e:
            log_error(e, {"operation": "_get_all_volumes"})
            raise
    
    async def _identify_unused_volumes(self, volumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify unused EBS volumes."""
        unused_volumes = []
        
        for volume in volumes:
            try:
                if await self._is_volume_unused(volume):
                    unused_volumes.append(volume)
            except Exception as e:
                log_error(e, {"volume_id": volume.get('VolumeId')})
                continue
        
        return unused_volumes
    
    async def _is_volume_unused(self, volume: Dict[str, Any]) -> bool:
        """Check if a volume is unused."""
        try:
            # Check if volume is attached
            if volume['State'] == 'in-use':
                return False
            
            # Check if volume is available (unattached)
            if volume['State'] == 'available':
                # Check creation time - if older than 30 days, consider unused
                creation_time = volume['CreateTime']
                if datetime.now(creation_time.tzinfo) - creation_time > timedelta(days=30):
                    return True
            
            # Check if volume has snapshots (don't delete if it does)
            if volume.get('SnapshotId'):
                return False
            
            # Check tags for protection
            tags = volume.get('Tags', [])
            for tag in tags:
                if tag['Key'].lower() in ['protected', 'keep', 'important']:
                    if tag['Value'].lower() in ['true', 'yes', '1']:
                        return False
            
            return True
            
        except Exception as e:
            log_error(e, {"volume_id": volume.get('VolumeId')})
            return False
    
    async def _delete_volumes(self, volumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Delete the specified volumes."""
        try:
            deleted_volumes = []
            
            for volume in volumes:
                try:
                    volume_id = volume['VolumeId']
                    
                    # Check if volume is still available
                    if volume['State'] == 'available':
                        self.client.delete_volume(VolumeId=volume_id)
                        deleted_volumes.append(volume)
                        
                        log_aws_operation(
                            "delete_volume",
                            "ec2",
                            settings.aws_region,
                            volume_id=volume_id
                        )
                    
                except Exception as e:
                    log_error(e, {"volume_id": volume.get('VolumeId')})
                    continue
            
            return deleted_volumes
            
        except Exception as e:
            log_error(e, {"operation": "_delete_volumes"})
            raise
    
    async def _calculate_volume_savings(self, volumes: List[Dict[str, Any]]) -> float:
        """Calculate estimated monthly savings from deleting volumes."""
        try:
            total_savings = 0.0
            
            for volume in volumes:
                size_gb = volume['Size']
                volume_type = volume['VolumeType']
                
                # Simplified pricing (in a real implementation, you'd use AWS Pricing API)
                pricing_per_gb = {
                    'gp2': 0.10,  # $0.10 per GB-month
                    'gp3': 0.08,  # $0.08 per GB-month
                    'io1': 0.125, # $0.125 per GB-month
                    'io2': 0.125, # $0.125 per GB-month
                    'st1': 0.045, # $0.045 per GB-month
                    'sc1': 0.015, # $0.015 per GB-month
                }
                
                price_per_gb = pricing_per_gb.get(volume_type, 0.10)
                monthly_cost = size_gb * price_per_gb
                total_savings += monthly_cost
            
            return total_savings
            
        except Exception as e:
            log_error(e, {"operation": "_calculate_volume_savings"})
            return 0.0
    
    async def migrate_gp2_to_gp3(self, dry_run: bool = False) -> ImplementationResponse:
        """Migrate GP2 volumes to GP3 for cost savings."""
        try:
            # Get all GP2 volumes
            volumes = await self._get_all_volumes()
            gp2_volumes = [vol for vol in volumes if vol['VolumeType'] == 'gp2']
            
            if not gp2_volumes:
                return ImplementationResponse(
                    success=True,
                    message="No GP2 volumes found",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                savings = await self._calculate_gp2_to_gp3_savings(gp2_volumes)
                return ImplementationResponse(
                    success=True,
                    message=f"Would migrate {len(gp2_volumes)} GP2 volumes to GP3",
                    savings=savings,
                    affected_resources=[vol['VolumeId'] for vol in gp2_volumes],
                    dry_run=dry_run
                )
            
            # In a real implementation, you would modify volume types
            # For now, we'll just return the dry run results
            savings = await self._calculate_gp2_to_gp3_savings(gp2_volumes)
            
            return ImplementationResponse(
                success=True,
                message=f"Identified {len(gp2_volumes)} GP2 volumes for migration to GP3",
                savings=savings,
                affected_resources=[vol['VolumeId'] for vol in gp2_volumes],
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "migrate_gp2_to_gp3"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to migrate GP2 volumes: {str(e)}",
                dry_run=dry_run
            )
    
    async def _calculate_gp2_to_gp3_savings(self, volumes: List[Dict[str, Any]]) -> float:
        """Calculate savings from migrating GP2 to GP3."""
        total_savings = 0.0
        
        for volume in volumes:
            size_gb = volume['Size']
            
            # GP2: $0.10 per GB-month, GP3: $0.08 per GB-month
            # Savings: $0.02 per GB-month
            savings_per_gb = 0.02
            monthly_savings = size_gb * savings_per_gb
            total_savings += monthly_savings
        
        return total_savings
    
    async def optimize_volume_types(self, dry_run: bool = False) -> ImplementationResponse:
        """Optimize EBS volume types for cost savings."""
        try:
            # Get all volumes
            volumes = await self._get_all_volumes()
            optimizable_volumes = await self._identify_optimizable_volumes(volumes)
            
            if not optimizable_volumes:
                return ImplementationResponse(
                    success=True,
                    message="No volumes found for optimization",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                savings = await self._calculate_optimization_savings(optimizable_volumes)
                return ImplementationResponse(
                    success=True,
                    message=f"Would optimize {len(optimizable_volumes)} volumes",
                    savings=savings,
                    affected_resources=[vol['VolumeId'] for vol in optimizable_volumes],
                    dry_run=dry_run
                )
            
            # In a real implementation, you would modify volume types
            savings = await self._calculate_optimization_savings(optimizable_volumes)
            
            return ImplementationResponse(
                success=True,
                message=f"Identified {len(optimizable_volumes)} volumes for optimization",
                savings=savings,
                affected_resources=[vol['VolumeId'] for vol in optimizable_volumes],
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "optimize_volume_types"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to optimize volumes: {str(e)}",
                dry_run=dry_run
            )
    
    async def _identify_optimizable_volumes(self, volumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify volumes that could be optimized."""
        optimizable = []
        
        for volume in volumes:
            volume_type = volume['VolumeType']
            
            # Check for expensive volume types that could be optimized
            if volume_type in ['io1', 'io2']:
                # Check if high IOPS are actually needed
                if volume.get('Iops', 0) < 1000:  # Low IOPS usage
                    optimizable.append(volume)
            
            # Check for large GP2 volumes that could be GP3
            elif volume_type == 'gp2' and volume['Size'] > 100:  # Large volumes
                optimizable.append(volume)
        
        return optimizable
    
    async def _calculate_optimization_savings(self, volumes: List[Dict[str, Any]]) -> float:
        """Calculate savings from volume optimization."""
        total_savings = 0.0
        
        for volume in volumes:
            volume_type = volume['VolumeType']
            size_gb = volume['Size']
            
            if volume_type in ['io1', 'io2']:
                # Migrate to GP3 for low IOPS volumes
                current_cost = size_gb * 0.125  # io1/io2 pricing
                new_cost = size_gb * 0.08  # GP3 pricing
                savings = current_cost - new_cost
                total_savings += savings
            
            elif volume_type == 'gp2':
                # Migrate to GP3
                savings_per_gb = 0.02
                savings = size_gb * savings_per_gb
                total_savings += savings
        
        return total_savings 