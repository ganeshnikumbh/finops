#!/usr/bin/env python3
"""
Automation Examples for AWS FinOps Application

This script demonstrates how to use the FinOps application
programmatically for automated cost optimization.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, List, Any
from datetime import datetime


class FinOpsClient:
    """Client for interacting with the FinOps application API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check application health."""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def get_recommendations(self) -> Dict[str, Any]:
        """Get Trusted Advisor recommendations."""
        async with self.session.get(f"{self.base_url}/recommendations") as response:
            return await response.json()
    
    async def implement_recommendation(self, check_id: str, dry_run: bool = True) -> Dict[str, Any]:
        """Implement a recommendation."""
        payload = {"dry_run": dry_run, "force": False}
        async with self.session.post(
            f"{self.base_url}/implement/{check_id}",
            json=payload
        ) as response:
            return await response.json()
    
    async def execute_automation(self, automation_id: str, dry_run: bool = True) -> Dict[str, Any]:
        """Execute a specific automation."""
        payload = {"dry_run": dry_run, "force": False}
        async with self.session.post(
            f"{self.base_url}/automations/{automation_id}/execute",
            json=payload
        ) as response:
            return await response.json()


async def example_1_health_check():
    """Example 1: Health check and status monitoring."""
    print("Example 1: Health Check and Status Monitoring")
    print("=" * 50)
    
    async with FinOpsClient() as client:
        try:
            health = await client.health_check()
            print(f"Application Status: {health['status']}")
            print(f"AWS Connection: {health['aws_connection']}")
            print(f"Last Check: {health['timestamp']}")
            print(f"Version: {health['version']}")
            
            if health['status'] == 'healthy' and health['aws_connection']:
                print("✓ Application is healthy and connected to AWS")
            else:
                print("✗ Application has issues")
                
        except Exception as e:
            print(f"Error checking health: {e}")


async def example_2_get_recommendations():
    """Example 2: Get and analyze recommendations."""
    print("\nExample 2: Get and Analyze Recommendations")
    print("=" * 50)
    
    async with FinOpsClient() as client:
        try:
            data = await client.get_recommendations()
            recommendations = data['recommendations']
            
            print(f"Total Recommendations: {data['total_count']}")
            print(f"Total Potential Savings: ${data['total_savings']:.2f}/month")
            print(f"Last Refresh: {data['last_refresh']}")
            
            # Categorize recommendations
            categories = {}
            statuses = {}
            implementable = 0
            
            for rec in recommendations:
                # Count by category
                category = rec['category']
                categories[category] = categories.get(category, 0) + 1
                
                # Count by status
                status = rec['status']
                statuses[status] = statuses.get(status, 0) + 1
                
                # Count implementable
                if rec['can_implement']:
                    implementable += 1
            
            print(f"\nBy Category:")
            for category, count in categories.items():
                print(f"  {category}: {count}")
            
            print(f"\nBy Status:")
            for status, count in statuses.items():
                print(f"  {status}: {count}")
            
            print(f"\nAuto-Implementable: {implementable}")
            
            # Show top savings opportunities
            print(f"\nTop Savings Opportunities:")
            sorted_recs = sorted(
                recommendations,
                key=lambda x: x.get('estimated_savings', 0),
                reverse=True
            )
            
            for i, rec in enumerate(sorted_recs[:5]):
                if rec.get('estimated_savings', 0) > 0:
                    print(f"  {i+1}. {rec['title']}: ${rec['estimated_savings']:.2f}/month")
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")


async def example_3_automated_cost_optimization():
    """Example 3: Automated cost optimization workflow."""
    print("\nExample 3: Automated Cost Optimization Workflow")
    print("=" * 50)
    
    async with FinOpsClient() as client:
        try:
            # Step 1: Get recommendations
            print("Step 1: Getting recommendations...")
            data = await client.get_recommendations()
            recommendations = data['recommendations']
            
            # Step 2: Filter for auto-implementable recommendations
            auto_implementable = [
                rec for rec in recommendations 
                if rec['can_implement'] and rec['status'] in ['warning', 'error']
            ]
            
            print(f"Found {len(auto_implementable)} auto-implementable recommendations")
            
            # Step 3: Execute automations
            total_savings = 0
            successful_implementations = 0
            
            for rec in auto_implementable:
                print(f"\nProcessing: {rec['title']}")
                print(f"  Estimated Savings: ${rec.get('estimated_savings', 0):.2f}/month")
                
                # First, do a dry run
                print("  Running dry run...")
                dry_run_result = await client.implement_recommendation(
                    rec['check_id'], 
                    dry_run=True
                )
                
                if dry_run_result['success']:
                    print(f"  Dry run successful: {dry_run_result['message']}")
                    
                    # Ask for confirmation (in real automation, you might have rules)
                    # For this example, we'll implement if savings > $10/month
                    if dry_run_result.get('savings', 0) > 10:
                        print("  Implementing (savings > $10/month)...")
                        result = await client.implement_recommendation(
                            rec['check_id'], 
                            dry_run=False
                        )
                        
                        if result['success']:
                            successful_implementations += 1
                            total_savings += result.get('savings', 0)
                            print(f"  ✓ Implementation successful: ${result.get('savings', 0):.2f}/month")
                        else:
                            print(f"  ✗ Implementation failed: {result['message']}")
                    else:
                        print("  Skipping (savings < $10/month)")
                else:
                    print(f"  ✗ Dry run failed: {dry_run_result['message']}")
            
            print(f"\nOptimization Summary:")
            print(f"  Successful Implementations: {successful_implementations}")
            print(f"  Total Monthly Savings: ${total_savings:.2f}")
            
        except Exception as e:
            print(f"Error in cost optimization: {e}")


async def example_4_scheduled_automation():
    """Example 4: Scheduled automation with specific targets."""
    print("\nExample 4: Scheduled Automation with Specific Targets")
    print("=" * 50)
    
    async with FinOpsClient() as client:
        try:
            # Define automation targets
            automation_targets = [
                {
                    'id': 'stop_idle_instances',
                    'name': 'Stop Idle EC2 Instances',
                    'max_savings': 100,  # Max $100/month per automation
                    'schedule': 'daily'
                },
                {
                    'id': 'delete_unused_volumes',
                    'name': 'Delete Unused EBS Volumes',
                    'max_savings': 50,
                    'schedule': 'weekly'
                },
                {
                    'id': 'enable_versioning',
                    'name': 'Enable S3 Versioning',
                    'max_savings': 0,  # Security improvement
                    'schedule': 'monthly'
                }
            ]
            
            print("Executing scheduled automations...")
            
            for target in automation_targets:
                print(f"\nProcessing: {target['name']}")
                print(f"  Schedule: {target['schedule']}")
                print(f"  Max Savings: ${target['max_savings']}/month")
                
                # Execute automation
                result = await client.execute_automation(
                    target['id'], 
                    dry_run=False
                )
                
                if result['success']:
                    savings = result.get('savings', 0)
                    print(f"  ✓ Success: {result['message']}")
                    print(f"  Actual Savings: ${savings:.2f}/month")
                    
                    # Check if within limits
                    if target['max_savings'] > 0 and savings > target['max_savings']:
                        print(f"  ⚠ Warning: Savings exceed limit (${savings:.2f} > ${target['max_savings']})")
                else:
                    print(f"  ✗ Failed: {result['message']}")
            
        except Exception as e:
            print(f"Error in scheduled automation: {e}")


async def example_5_monitoring_and_alerting():
    """Example 5: Monitoring and alerting system."""
    print("\nExample 5: Monitoring and Alerting System")
    print("=" * 50)
    
    async with FinOpsClient() as client:
        try:
            # Get current state
            data = await client.get_recommendations()
            recommendations = data['recommendations']
            
            # Calculate metrics
            total_savings = data['total_savings']
            critical_issues = len([r for r in recommendations if r['status'] == 'error'])
            warnings = len([r for r in recommendations if r['status'] == 'warning'])
            auto_fixable = len([r for r in recommendations if r['can_implement']])
            
            print(f"Current Metrics:")
            print(f"  Total Potential Savings: ${total_savings:.2f}/month")
            print(f"  Critical Issues: {critical_issues}")
            print(f"  Warnings: {warnings}")
            print(f"  Auto-Fixable: {auto_fixable}")
            
            # Define alert thresholds
            alerts = []
            
            if total_savings > 500:
                alerts.append(f"HIGH: Potential savings exceed $500/month (${total_savings:.2f})")
            
            if critical_issues > 5:
                alerts.append(f"CRITICAL: {critical_issues} critical issues detected")
            
            if warnings > 10:
                alerts.append(f"WARNING: {warnings} warnings detected")
            
            if auto_fixable > 0:
                alerts.append(f"INFO: {auto_fixable} issues can be auto-fixed")
            
            # Generate report
            print(f"\nAlert Summary:")
            if alerts:
                for alert in alerts:
                    print(f"  {alert}")
            else:
                print("  No alerts - system is healthy")
            
            # Simulate automated response
            if auto_fixable > 0 and total_savings > 100:
                print(f"\nAutomated Response:")
                print("  Triggering cost optimization workflow...")
                
                # In a real system, you would trigger the automation here
                # For this example, we'll just show what would happen
                print("  ✓ Would execute auto-fixable recommendations")
                print(f"  ✓ Expected savings: ${total_savings * 0.8:.2f}/month (80% of potential)")
            
        except Exception as e:
            print(f"Error in monitoring: {e}")


async def main():
    """Run all automation examples."""
    print("AWS FinOps Application - Automation Examples")
    print("=" * 60)
    
    # Check if application is running
    try:
        async with FinOpsClient() as client:
            health = await client.health_check()
            if health['status'] != 'healthy':
                print("Error: FinOps application is not healthy")
                print("Please start the application first:")
                print("  cd backend && uvicorn app.main:app --reload")
                return
    except Exception as e:
        print(f"Error: Cannot connect to FinOps application: {e}")
        print("Please ensure the application is running on http://localhost:8000")
        return
    
    # Run examples
    await example_1_health_check()
    await example_2_get_recommendations()
    await example_3_automated_cost_optimization()
    await example_4_scheduled_automation()
    await example_5_monitoring_and_alerting()
    
    print("\n" + "=" * 60)
    print("Automation Examples Completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 