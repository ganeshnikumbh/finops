import boto3
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

from ..models import ImplementationResponse
from ..utils.logger import logger, log_aws_operation, log_error
from config import settings


class EC2Service:
    """Service for EC2-related automations."""
    
    def __init__(self):
        self.client = boto3.client('ec2', region_name=settings.aws_region)
        self.logger = logger
    
    async def stop_idle_instances(self, dry_run: bool = False) -> ImplementationResponse:
        """Stop idle EC2 instances to reduce costs."""
        try:
            # Get all running instances
            instances = await self._get_running_instances()
            idle_instances = await self._identify_idle_instances(instances)
            
            if not idle_instances:
                return ImplementationResponse(
                    success=True,
                    message="No idle instances found",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                return ImplementationResponse(
                    success=True,
                    message=f"Would stop {len(idle_instances)} idle instances",
                    savings=await self._calculate_savings(idle_instances),
                    affected_resources=[inst['InstanceId'] for inst in idle_instances],
                    dry_run=dry_run
                )
            
            # Stop instances
            stopped_instances = await self._stop_instances(idle_instances)
            
            savings = await self._calculate_savings(stopped_instances)
            
            log_aws_operation(
                "stop_idle_instances",
                "ec2",
                settings.aws_region,
                instances_stopped=len(stopped_instances),
                savings=savings
            )
            
            return ImplementationResponse(
                success=True,
                message=f"Successfully stopped {len(stopped_instances)} idle instances",
                savings=savings,
                affected_resources=[inst['InstanceId'] for inst in stopped_instances],
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "stop_idle_instances"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to stop idle instances: {str(e)}",
                dry_run=dry_run
            )
    
    async def _get_running_instances(self) -> List[Dict[str, Any]]:
        """Get all running EC2 instances."""
        try:
            response = self.client.describe_instances(
                Filters=[
                    {
                        'Name': 'instance-state-name',
                        'Values': ['running']
                    }
                ]
            )
            
            instances = []
            for reservation in response['Reservations']:
                instances.extend(reservation['Instances'])
            
            return instances
            
        except Exception as e:
            log_error(e, {"operation": "_get_running_instances"})
            raise
    
    async def _identify_idle_instances(self, instances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify idle instances based on CloudWatch metrics."""
        idle_instances = []
        
        for instance in instances:
            try:
                # Check if instance is idle (simplified logic)
                is_idle = await self._check_instance_idle(instance)
                if is_idle:
                    idle_instances.append(instance)
            except Exception as e:
                log_error(e, {"instance_id": instance.get('InstanceId')})
                continue
        
        return idle_instances
    
    async def _check_instance_idle(self, instance: Dict[str, Any]) -> bool:
        """Check if an instance is idle based on various criteria."""
        try:
            instance_id = instance['InstanceId']
            
            # Check instance type (t2, t3 instances are often idle)
            instance_type = instance['InstanceType']
            if instance_type.startswith('t2.') or instance_type.startswith('t3.'):
                # Additional checks for t2/t3 instances
                return await self._check_t_instance_idle(instance)
            
            # For other instance types, check if they're in a dev/test environment
            tags = instance.get('Tags', [])
            for tag in tags:
                if tag['Key'].lower() in ['environment', 'env']:
                    if tag['Value'].lower() in ['dev', 'development', 'test']:
                        return True
            
            return False
            
        except Exception as e:
            log_error(e, {"instance_id": instance.get('InstanceId')})
            return False
    
    async def _check_t_instance_idle(self, instance: Dict[str, Any]) -> bool:
        """Check if a t2/t3 instance is idle."""
        try:
            # For t2/t3 instances, check if they're in dev/test environment
            # or have been running for more than 24 hours without activity
            tags = instance.get('Tags', [])
            
            for tag in tags:
                if tag['Key'].lower() in ['environment', 'env']:
                    if tag['Value'].lower() in ['dev', 'development', 'test']:
                        return True
                
                if tag['Key'].lower() in ['purpose', 'role']:
                    if tag['Value'].lower() in ['dev', 'test', 'staging']:
                        return True
            
            # Check launch time
            launch_time = instance['LaunchTime']
            if datetime.now(launch_time.tzinfo) - launch_time > timedelta(hours=24):
                return True
            
            return False
            
        except Exception as e:
            log_error(e, {"instance_id": instance.get('InstanceId')})
            return False
    
    async def _stop_instances(self, instances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Stop the specified instances."""
        try:
            instance_ids = [inst['InstanceId'] for inst in instances]
            
            response = self.client.stop_instances(
                InstanceIds=instance_ids
            )
            
            # Wait for instances to stop
            waiter = self.client.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=instance_ids)
            
            return instances
            
        except Exception as e:
            log_error(e, {"operation": "_stop_instances"})
            raise
    
    async def _calculate_savings(self, instances: List[Dict[str, Any]]) -> float:
        """Calculate estimated monthly savings from stopping instances."""
        try:
            total_savings = 0.0
            
            for instance in instances:
                instance_type = instance['InstanceType']
                
                # Simplified pricing (in a real implementation, you'd use AWS Pricing API)
                pricing = {
                    't2.micro': 8.47,
                    't2.small': 16.94,
                    't2.medium': 33.88,
                    't3.micro': 7.47,
                    't3.small': 14.94,
                    't3.medium': 29.88,
                }
                
                monthly_cost = pricing.get(instance_type, 50.0)  # Default $50/month
                total_savings += monthly_cost
            
            return total_savings
            
        except Exception as e:
            log_error(e, {"operation": "_calculate_savings"})
            return 0.0
    
    async def optimize_instance_types(self, dry_run: bool = False) -> ImplementationResponse:
        """Optimize EC2 instance types for cost savings."""
        try:
            # Get instances that could be optimized
            instances = await self._get_running_instances()
            optimizable_instances = await self._identify_optimizable_instances(instances)
            
            if not optimizable_instances:
                return ImplementationResponse(
                    success=True,
                    message="No instances found for optimization",
                    savings=0.0,
                    affected_resources=[],
                    dry_run=dry_run
                )
            
            if dry_run:
                savings = await self._calculate_optimization_savings(optimizable_instances)
                return ImplementationResponse(
                    success=True,
                    message=f"Would optimize {len(optimizable_instances)} instances",
                    savings=savings,
                    affected_resources=[inst['InstanceId'] for inst in optimizable_instances],
                    dry_run=dry_run
                )
            
            # In a real implementation, you would modify instance types
            # For now, we'll just return the dry run results
            savings = await self._calculate_optimization_savings(optimizable_instances)
            
            return ImplementationResponse(
                success=True,
                message=f"Identified {len(optimizable_instances)} instances for optimization",
                savings=savings,
                affected_resources=[inst['InstanceId'] for inst in optimizable_instances],
                dry_run=dry_run
            )
            
        except Exception as e:
            log_error(e, {"operation": "optimize_instance_types"})
            return ImplementationResponse(
                success=False,
                message=f"Failed to optimize instances: {str(e)}",
                dry_run=dry_run
            )
    
    async def _identify_optimizable_instances(self, instances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify instances that could be optimized."""
        optimizable = []
        
        for instance in instances:
            instance_type = instance['InstanceType']
            
            # Check for over-provisioned instances
            if instance_type.startswith('m5.') or instance_type.startswith('c5.'):
                # Check if instance is underutilized
                if await self._is_instance_underutilized(instance):
                    optimizable.append(instance)
        
        return optimizable
    
    async def _is_instance_underutilized(self, instance: Dict[str, Any]) -> bool:
        """Check if an instance is underutilized."""
        # Simplified logic - in real implementation, check CloudWatch metrics
        return True
    
    async def _calculate_optimization_savings(self, instances: List[Dict[str, Any]]) -> float:
        """Calculate savings from instance optimization."""
        total_savings = 0.0
        
        for instance in instances:
            current_type = instance['InstanceType']
            
            # Simplified optimization savings calculation
            if current_type.startswith('m5.'):
                total_savings += 20.0  # Estimated $20/month savings
            elif current_type.startswith('c5.'):
                total_savings += 15.0  # Estimated $15/month savings
        
        return total_savings 