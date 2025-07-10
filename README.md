# AI Medical Billing System

A comprehensive HIPAA-compliant AI-powered medical billing application featuring 8 specialized agents for complete end-to-end billing automation across all medical specialties.

## 🏥 Overview

This system automates the entire medical billing workflow using advanced AI technologies including OCR, NLP, machine learning, and Retrieval-Augmented Generation (RAG). Built with Python, FastAPI, and modern AI frameworks, it provides a secure, scalable, and compliant solution for healthcare providers.

## 🤖 The 8 AI Agents

### 1. Patient Registration and Insurance Verification Agent
- **OCR Processing**: Extracts patient data from intake forms and insurance cards
- **Real-time Eligibility**: Verifies insurance coverage and benefits
- **EHR Integration**: Creates and updates patient records via HL7 FHIR APIs
- **Data Validation**: Ensures accuracy and completeness of patient information

### 2. Medical Coding Agent
- **NLP Processing**: Analyzes clinical notes and documentation
- **RAG Implementation**: Uses vector databases of medical knowledge for accurate coding
- **Code Assignment**: Predicts ICD-10-CM, CPT, and HCPCS codes
- **Compliance Checking**: Ensures coding follows official guidelines

### 3. Claim Submission Agent
- **Claim Generation**: Creates clean, complete claims in standard formats
- **Electronic Submission**: Submits claims via EDI or clearinghouse APIs
- **Error Detection**: Pre-submission validation to prevent denials
- **Status Tracking**: Monitors submission acknowledgments

### 4. Claim Follow-up and Denial Management Agent
- **Automated Monitoring**: Tracks claim status and identifies delays
- **Denial Analysis**: Categorizes and prioritizes denials
- **Appeal Generation**: Creates appeal letters and documentation
- **Pattern Recognition**: Learns from denial patterns to prevent future issues

### 5. Patient Billing and Collections Agent
- **Statement Generation**: Creates patient-friendly bills
- **Payment Processing**: Integrates with payment gateways
- **Automated Reminders**: Sends payment reminders via multiple channels
- **Collections Management**: Manages overdue accounts and payment plans

### 6. Financial Reporting and Analysis Agent
- **Performance Dashboards**: Real-time financial metrics and KPIs
- **Predictive Analytics**: Forecasts cash flow and identifies trends
- **Denial Analysis**: Provides insights to improve claim success rates
- **Compliance Reporting**: Generates required regulatory reports

### 7. Patient Records and Data Integrity Agent
- **Data Synchronization**: Maintains consistency between EHR and billing systems
- **Quality Audits**: Identifies and corrects data inconsistencies
- **Charge Capture**: Ensures all services are properly documented and billed
- **Archive Management**: Handles record retention and compliance

### 8. Communication and Collaboration Agent
- **Patient Chatbot**: 24/7 support for billing inquiries
- **Payer Communication**: Automates interactions with insurance companies
- **Internal Coordination**: Facilitates communication between departments
- **Multi-channel Support**: Handles phone, email, SMS, and chat interactions

## 🏗️ Architecture

### CrewAI Framework

The system is built on **CrewAI**, a cutting-edge framework for orchestrating autonomous AI agents:

- **MedicalBillingCrew**: Main orchestrator managing all 8 specialized agents
- **MedicalBillingAgent**: HIPAA-compliant wrapper for CrewAI agents with audit logging
- **Specialized Crews**: Pre-configured teams for different workflows:
  - **Patient Intake Crew**: Registration + Data Integrity agents
  - **Claim Processing Crew**: Coding + Submission + Follow-up agents  
  - **Patient Financial Crew**: Billing + Communication agents
  - **Analytics Crew**: Reporting + Data Integrity agents
- **Custom Tools**: 20+ specialized tools for medical billing operations
- **Task Orchestration**: Sequential and parallel task execution with dependencies

### Technology Stack

- **AI Framework**: CrewAI, LangChain for agent orchestration
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **AI/ML**: PyTorch, Transformers, LangChain, ChromaDB, OpenAI/Azure OpenAI
- **Database**: PostgreSQL, Redis
- **OCR**: Tesseract, OpenCV, PIL
- **Security**: Cryptography, Encryption at rest and in transit
- **Communication**: Twilio (SMS), SendGrid (Email), Stripe (Payments)
- **Monitoring**: Prometheus, Structured Logging, Sentry
- **Deployment**: Docker, Kubernetes, Cloud-native

### Security & Compliance

- **HIPAA Compliant**: End-to-end encryption, audit logging, access controls
- **Data Encryption**: PHI encrypted at rest using AES-256
- **Audit Trails**: Comprehensive logging of all data access and modifications
- **Role-based Access**: Granular permissions and user management
- **Secure APIs**: JWT authentication, rate limiting, input validation

### Integration Capabilities

- **EHR Systems**: HL7 FHIR R4 compliant
- **Clearinghouses**: EDI 837/835/277 transactions
- **Payment Processors**: Stripe, PayPal, healthcare-specific gateways
- **Cloud Services**: AWS, Azure, GCP with HIPAA-eligible services

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-medical-billing-app
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
# Create database
createdb medical_billing

# Run migrations
alembic upgrade head
```

6. **Start the application**
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app
```

## 📋 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/medical_billing
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# AI Services
OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint

# Communication
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
SENDGRID_API_KEY=your-sendgrid-key

# Payment Processing
STRIPE_SECRET_KEY=your-stripe-key

# EHR Integration
FHIR_BASE_URL=your-fhir-endpoint
FHIR_CLIENT_ID=your-fhir-client-id
FHIR_CLIENT_SECRET=your-fhir-secret
```

## 🤖 Using the CrewAI System

### Quick Start with CrewAI

```python
from app.agents.base import MedicalBillingCrew
from app.agents.registration import create_patient_registration_agent

# Initialize the crew
crew = MedicalBillingCrew()

# Create specialized agents
registration_agent = create_patient_registration_agent(crew)

# Execute individual agent tasks
result = await crew.execute_agent_task(
    "patient_registration_agent",
    "Process patient intake form at /path/to/form.pdf and extract demographic data",
    {"user_id": "admin", "patient_id": "P001"}
)

# Execute crew workflows
result = await crew.execute_crew_task(
    "patient_intake_crew",
    "Complete patient registration workflow for new patient John Smith"
)
```

### Running the Demonstration

```bash
# Run the comprehensive demo
python demo_crewai_system.py
```

This demo showcases:
- Patient registration with OCR and eligibility verification
- Medical coding with NLP and RAG
- Claim generation and submission
- Denial analysis and appeal generation
- Multi-agent crew collaboration

## 🔧 API Usage

### Authentication

All API endpoints require authentication via Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.yourdomain.com/api/v1/patients
```

### CrewAI API Endpoints

#### Execute Agent Task
```bash
POST /api/v1/crew/agents/{agent_id}/execute
{
  "task_description": "Process patient intake form and extract data",
  "context": {
    "user_id": "admin",
    "patient_id": "P001"
  }
}
```

#### Execute Crew Workflow
```bash
POST /api/v1/crew/{crew_name}/execute
{
  "task_description": "Complete end-to-end claim processing",
  "context": {
    "patient_id": "P001",
    "encounter_id": "E001"
  }
}
```

#### Get Agent Status
```bash
GET /api/v1/crew/agents/{agent_id}/status
```

#### List Available Crews
```bash
GET /api/v1/crew/crews
```

### Legacy API Calls

#### Execute Agent Task (Legacy)
```bash
POST /api/v1/agents/execute
{
  "agent_type": "registration",
  "action": "extract_patient_data",
  "parameters": {
    "document_path": "/path/to/intake_form.pdf",
    "document_type": "intake_form"
  }
}
```

#### Check Agent Status
```bash
GET /api/v1/agents/status
```

#### Process Insurance Card
```bash
POST /api/v1/agents/execute
{
  "agent_type": "registration",
  "action": "process_insurance_card",
  "parameters": {
    "card_image_path": "/path/to/insurance_card.jpg",
    "card_side": "front"
  }
}
```

## 📊 Features

### Core Capabilities

- ✅ **OCR Processing**: Extract data from forms, insurance cards, and documents
- ✅ **Real-time Eligibility**: Verify insurance coverage and benefits
- ✅ **AI-Powered Coding**: Automated medical code assignment with high accuracy
- ✅ **Electronic Claims**: Submit and track claims electronically
- ✅ **Denial Management**: Automated denial analysis and appeal generation
- ✅ **Patient Billing**: Generate bills and process payments
- ✅ **Financial Analytics**: Real-time reporting and predictive insights
- ✅ **Data Integrity**: Maintain consistency across systems
- ✅ **24/7 Chatbot**: Patient support and communication

### Advanced Features

- 🔄 **Multi-Agent Orchestration**: Coordinated workflow between agents
- 🧠 **Machine Learning**: Continuous improvement through pattern recognition
- 🔍 **RAG Implementation**: Knowledge-grounded AI responses
- 📈 **Predictive Analytics**: Cash flow forecasting and trend analysis
- 🔐 **HIPAA Compliance**: Enterprise-grade security and audit trails
- 🌐 **Multi-Specialty Support**: Works across all medical specialties
- ⚡ **Real-time Processing**: Immediate results for critical workflows
- 📱 **Multi-channel Communication**: SMS, email, voice, and chat support

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/agents/
pytest tests/api/
pytest tests/utils/
```

## 📈 Monitoring

### Health Checks
- `GET /health` - System health status
- `GET /metrics` - Performance metrics
- `GET /api/v1/agents/status` - Agent status

### Logging
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Audit logs: `logs/audit.log`
- Agent logs: `logs/agents.log`

### Metrics
- Agent performance metrics
- API response times
- System resource usage
- Business KPIs

## 🔒 Security

### Data Protection
- AES-256 encryption for PHI at rest
- TLS 1.3 for data in transit
- Key rotation and management
- Secure file storage

### Access Control
- JWT-based authentication
- Role-based permissions
- API rate limiting
- IP whitelisting

### Audit Compliance
- Comprehensive audit trails
- User activity logging
- Data access tracking
- Compliance reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full API documentation](https://docs.yourdomain.com)
- **Issues**: [GitHub Issues](https://github.com/yourorg/ai-medical-billing/issues)
- **Email**: support@yourdomain.com
- **Phone**: 1-800-MEDICAL

## 🗺️ Roadmap

### Q1 2024
- [ ] Integration with major EHR systems (Epic, Cerner, allscripts)
- [ ] Advanced ML models for specialty-specific coding
- [ ] Multi-language support

### Q2 2024
- [ ] Voice-to-text integration for clinical notes
- [ ] Real-time collaboration features
- [ ] Enhanced analytics dashboard

### Q3 2024
- [ ] Mobile applications for iOS and Android
- [ ] Blockchain integration for audit trails
- [ ] Advanced fraud detection

### Q4 2024
- [ ] International medical coding standards
- [ ] AI-powered contract negotiation
- [ ] Population health analytics

## 📋 System Requirements

### Minimum Requirements
- CPU: 4 cores, 2.0 GHz
- RAM: 8 GB
- Storage: 100 GB SSD
- Network: 100 Mbps

### Recommended Requirements
- CPU: 8 cores, 3.0 GHz
- RAM: 32 GB
- Storage: 500 GB NVMe SSD
- Network: 1 Gbps
- GPU: NVIDIA RTX 3080 (for AI processing)

### Cloud Deployment
- AWS: t3.xlarge or larger
- Azure: Standard_D4s_v3 or larger
- GCP: n1-standard-4 or larger

---

**Built with ❤️ for healthcare providers worldwide** 