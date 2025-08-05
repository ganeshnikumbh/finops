# AWS FinOps Application using Trusted Advisor

A comprehensive FinOps web application that visualizes and implements AWS Trusted Advisor recommendations. Built with Vue.js 3 frontend and FastAPI backend.

## Features

- **Trusted Advisor Integration**: Fetch and display AWS Trusted Advisor checks and recommendations
- **Automation Engine**: Implement automated fixes for common cost optimization issues
- **Real-time Monitoring**: Track cost savings and resource optimization
- **Modern UI**: Clean, responsive interface built with Vue.js 3

## Supported Automations

- Stop idle EC2 instances
- Delete unused EBS volumes
- Enable versioning on S3 buckets
- Remove unattached EBS volumes
- Optimize RDS instances

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **boto3**: AWS SDK for Python
- **asyncio**: Asynchronous programming for better performance
- **pydantic**: Data validation and settings management
- **uvicorn**: ASGI server for FastAPI

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Axios**: HTTP client for API calls
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and dev server

## Project Structure

```
finops/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── trusted_advisor.py
│   │   │   ├── ec2_service.py
│   │   │   ├── ebs_service.py
│   │   │   └── s3_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py
│   ├── requirements.txt
│   └── config.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RecommendationList.vue
│   │   │   ├── RecommendationCard.vue
│   │   │   └── LoadingSpinner.vue
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── scripts/
│   ├── setup_aws.py
│   └── automation_examples.py
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- AWS CLI configured with appropriate permissions
- AWS Trusted Advisor access

## Setup Instructions

### 1. Clone and Setup

```bash
git clone <repository-url>
cd finops
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. AWS Configuration

Ensure your AWS credentials are configured:

```bash
aws configure
```

Required AWS permissions:
- `support:*` (for Trusted Advisor)
- `ec2:*` (for EC2 operations)
- `s3:*` (for S3 operations)
- `rds:*` (for RDS operations)

### 5. Environment Variables

Create a `.env` file in the backend directory:

```env
AWS_REGION=us-east-1
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

## Running the Application

### 1. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

### GET /recommendations
Returns list of Trusted Advisor checks and summaries.

**Response:**
```json
{
  "recommendations": [
    {
      "check_id": "string",
      "category": "Cost Optimization",
      "title": "Idle EC2 Instances",
      "description": "Stop idle EC2 instances to reduce costs",
      "status": "WARNING",
      "estimated_savings": 150.00,
      "can_implement": true
    }
  ]
}
```

### POST /implement/{check_id}
Executes automation for the specified check.

**Response:**
```json
{
  "success": true,
  "message": "Successfully stopped 3 idle EC2 instances",
  "savings": 45.00,
  "affected_resources": ["i-1234567890abcdef0"]
}
```

## Automation Examples

The application includes several automation scripts:

1. **EC2 Idle Instance Stopper**: Identifies and stops idle EC2 instances
2. **EBS Volume Cleanup**: Removes unattached EBS volumes
3. **S3 Versioning Enabler**: Enables versioning on S3 buckets
4. **RDS Optimization**: Identifies underutilized RDS instances

## Security Considerations

- All AWS operations use IAM roles and permissions
- API endpoints include proper error handling
- Sensitive data is not logged
- CORS is properly configured
- Input validation on all endpoints

## Monitoring and Logging

- Structured logging with different levels
- AWS CloudWatch integration
- Performance metrics tracking
- Error tracking and alerting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for debugging information 