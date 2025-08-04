#!/usr/bin/env python3
"""
AWS Setup Script for FinOps Application

This script helps configure AWS credentials and test the connection
for the FinOps application.
"""

import boto3
import os
import sys
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from typing import Dict, Any


def check_aws_credentials() -> Dict[str, Any]:
    """Check if AWS credentials are properly configured."""
    result = {
        'configured': False,
        'method': None,
        'region': None,
        'profile': None,
        'error': None
    }
    
    try:
        # Try to get session info
        session = boto3.Session()
        
        # Check credentials
        credentials = session.get_credentials()
        if credentials:
            result['configured'] = True
            result['method'] = 'session'
        
        # Check region
        region = session.region_name
        if region:
            result['region'] = region
        else:
            result['region'] = 'us-east-1'  # Default
        
        # Check if using a profile
        profile = session.profile_name
        if profile:
            result['profile'] = profile
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        return result


def test_aws_services() -> Dict[str, Any]:
    """Test AWS service connections."""
    services = {
        'ec2': False,
        's3': False,
        'support': False,
        'rds': False
    }
    
    try:
        # Test EC2
        ec2_client = boto3.client('ec2')
        ec2_client.describe_regions()
        services['ec2'] = True
        print("✓ EC2 connection successful")
    except Exception as e:
        print(f"✗ EC2 connection failed: {e}")
    
    try:
        # Test S3
        s3_client = boto3.client('s3')
        s3_client.list_buckets()
        services['s3'] = True
        print("✓ S3 connection successful")
    except Exception as e:
        print(f"✗ S3 connection failed: {e}")
    
    try:
        # Test Support (Trusted Advisor)
        support_client = boto3.client('support')
        support_client.describe_trusted_advisor_checks(language='en')
        services['support'] = True
        print("✓ Trusted Advisor connection successful")
    except Exception as e:
        print(f"✗ Trusted Advisor connection failed: {e}")
    
    try:
        # Test RDS
        rds_client = boto3.client('rds')
        rds_client.describe_db_instances()
        services['rds'] = True
        print("✓ RDS connection successful")
    except Exception as e:
        print(f"✗ RDS connection failed: {e}")
    
    return services


def check_required_permissions() -> Dict[str, bool]:
    """Check if required AWS permissions are available."""
    permissions = {
        'support:*': False,
        'ec2:*': False,
        's3:*': False,
        'rds:*': False
    }
    
    try:
        # Test Trusted Advisor permissions
        support_client = boto3.client('support')
        support_client.describe_trusted_advisor_checks(language='en')
        permissions['support:*'] = True
        print("✓ Trusted Advisor permissions OK")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print("✗ Trusted Advisor permissions denied")
        else:
            print(f"✗ Trusted Advisor error: {e}")
    
    try:
        # Test EC2 permissions
        ec2_client = boto3.client('ec2')
        ec2_client.describe_instances()
        permissions['ec2:*'] = True
        print("✓ EC2 permissions OK")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print("✗ EC2 permissions denied")
        else:
            print(f"✗ EC2 error: {e}")
    
    try:
        # Test S3 permissions
        s3_client = boto3.client('s3')
        s3_client.list_buckets()
        permissions['s3:*'] = True
        print("✓ S3 permissions OK")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print("✗ S3 permissions denied")
        else:
            print(f"✗ S3 error: {e}")
    
    try:
        # Test RDS permissions
        rds_client = boto3.client('rds')
        rds_client.describe_db_instances()
        permissions['rds:*'] = True
        print("✓ RDS permissions OK")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print("✗ RDS permissions denied")
        else:
            print(f"✗ RDS error: {e}")
    
    return permissions


def create_env_file():
    """Create a .env file with AWS configuration."""
    env_content = """# AWS FinOps Application Environment Variables

# AWS Configuration
AWS_REGION=us-east-1

# Application Configuration
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# Optional: Override AWS credentials (not recommended for production)
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False


def main():
    """Main setup function."""
    print("AWS FinOps Application Setup")
    print("=" * 40)
    
    # Check AWS credentials
    print("\n1. Checking AWS credentials...")
    creds = check_aws_credentials()
    
    if creds['configured']:
        print(f"✓ AWS credentials configured via {creds['method']}")
        if creds['profile']:
            print(f"  Using profile: {creds['profile']}")
        print(f"  Region: {creds['region']}")
    else:
        print("✗ AWS credentials not configured")
        print("  Please run: aws configure")
        print("  Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        return False
    
    # Test AWS services
    print("\n2. Testing AWS service connections...")
    services = test_aws_services()
    
    # Check permissions
    print("\n3. Checking required permissions...")
    permissions = check_required_permissions()
    
    # Create .env file
    print("\n4. Creating environment file...")
    create_env_file()
    
    # Summary
    print("\n" + "=" * 40)
    print("SETUP SUMMARY")
    print("=" * 40)
    
    print(f"AWS Credentials: {'✓' if creds['configured'] else '✗'}")
    print(f"Region: {creds['region']}")
    
    print("\nService Connections:")
    for service, status in services.items():
        print(f"  {service.upper()}: {'✓' if status else '✗'}")
    
    print("\nRequired Permissions:")
    for permission, status in permissions.items():
        print(f"  {permission}: {'✓' if status else '✗'}")
    
    # Check if all required services are working
    required_services = ['ec2', 's3', 'support']
    all_services_ok = all(services.get(service, False) for service in required_services)
    
    if all_services_ok:
        print("\n✓ Setup completed successfully!")
        print("You can now run the FinOps application.")
        return True
    else:
        print("\n✗ Setup incomplete. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 