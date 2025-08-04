# AWS FinOps Application - Quick Start Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- AWS CLI configured with appropriate permissions

### 1. Setup AWS Credentials
```bash
aws configure
```

### 2. Run Setup Script
```bash
python scripts/setup_aws.py
```

### 3. Start the Application
```bash
python start.py
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
finops/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Main FastAPI application
│   │   ├── models.py       # Pydantic models
│   │   ├── services/       # AWS service integrations
│   │   └── utils/          # Utilities and logging
│   ├── requirements.txt    # Python dependencies
│   └── config.py          # Configuration
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── services/       # API service
│   │   └── App.vue         # Main app component
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
├── scripts/                # Utility scripts
│   ├── setup_aws.py        # AWS setup script
│   └── automation_examples.py # Automation examples
├── start.py                # Application startup script
└── README.md               # Detailed documentation
```

## 🔧 Manual Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Key Features

### Backend API Endpoints
- `GET /recommendations` - Get Trusted Advisor recommendations
- `POST /implement/{check_id}` - Implement a recommendation
- `GET /health` - Health check
- `GET /automations/available` - List available automations
- `POST /automations/{id}/execute` - Execute specific automation

### Supported Automations
- **EC2**: Stop idle instances, optimize instance types
- **EBS**: Delete unused volumes, migrate GP2 to GP3
- **S3**: Enable versioning, enable logging, remove public access
- **RDS**: Optimize database instances

### Frontend Features
- Real-time recommendation display
- Interactive implementation buttons
- Filtering and sorting
- Health status monitoring
- Responsive design

## 🔒 Security Considerations

- All AWS operations use IAM roles and permissions
- API endpoints include proper error handling
- CORS is properly configured
- Input validation on all endpoints
- Structured logging for audit trails

## 📊 Monitoring

- Health checks every 30 seconds
- Structured logging with different levels
- Performance metrics tracking
- Error tracking and alerting

## 🚨 Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   ```bash
   aws configure
   ```

2. **Trusted Advisor Access Denied**
   - Ensure your AWS account has Trusted Advisor access
   - Check IAM permissions for `support:*`

3. **Port Already in Use**
   - Backend: Change port in `uvicorn` command
   - Frontend: Change port in `vite.config.js`

4. **Node.js Dependencies**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Debug Mode
```bash
# Backend with debug logging
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Frontend with verbose output
cd frontend && npm run dev -- --debug
```

## 📈 Usage Examples

### Using the API
```bash
# Get recommendations
curl http://localhost:8000/recommendations

# Implement a recommendation (dry run)
curl -X POST http://localhost:8000/implement/check_id \
  -H "Content-Type: application/json" \
  -d '{"dry_run": true}'

# Execute automation
curl -X POST http://localhost:8000/automations/stop_idle_instances/execute \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

### Running Automation Examples
```bash
python scripts/automation_examples.py
```

## 🔄 Development

### Adding New Automations
1. Create service in `backend/app/services/`
2. Add implementation mapping in `main.py`
3. Update frontend API service
4. Add UI components

### Testing
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm run test
```

## 📚 Additional Resources

- [AWS Trusted Advisor Documentation](https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [AWS FinOps Best Practices](https://aws.amazon.com/finops/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details 