"""
Configuration settings for the AI Medical Billing Application
"""

import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "AI Medical Billing System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    HOST: str = Field(default="127.0.0.1", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./medical_billing.db", env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Encryption for PHI
    ENCRYPTION_KEY: str = Field(default="dev-encryption-key-change-in-production", env="ENCRYPTION_KEY")
    
    # AI/ML Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    AZURE_OPENAI_API_KEY: Optional[str] = Field(default=None, env="AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(default=None, env="AZURE_OPENAI_ENDPOINT")
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    
    # OCR Configuration
    TESSERACT_PATH: Optional[str] = Field(default=None, env="TESSERACT_PATH")
    
    # Communication Services
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    
    SENDGRID_API_KEY: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL: Optional[str] = Field(default=None, env="SENDGRID_FROM_EMAIL")
    
    # Payment Processing
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    
    # EDI and Clearinghouse
    CLEARINGHOUSE_API_URL: Optional[str] = Field(default=None, env="CLEARINGHOUSE_API_URL")
    CLEARINGHOUSE_API_KEY: Optional[str] = Field(default=None, env="CLEARINGHOUSE_API_KEY")
    
    # EHR Integration
    FHIR_BASE_URL: Optional[str] = Field(default=None, env="FHIR_BASE_URL")
    FHIR_CLIENT_ID: Optional[str] = Field(default=None, env="FHIR_CLIENT_ID")
    FHIR_CLIENT_SECRET: Optional[str] = Field(default=None, env="FHIR_CLIENT_SECRET")
    
    # Cloud Storage
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: Optional[str] = Field(default=None, env="AWS_REGION")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Compliance and Audit
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=2555, env="AUDIT_LOG_RETENTION_DAYS")  # 7 years
    HIPAA_COMPLIANCE_MODE: bool = Field(default=True, env="HIPAA_COMPLIANCE_MODE")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    PROMETHEUS_METRICS_PATH: str = Field(default="/metrics", env="PROMETHEUS_METRICS_PATH")
    
    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = Field(default=10, env="MAX_CONCURRENT_AGENTS")
    AGENT_TIMEOUT_SECONDS: int = Field(default=300, env="AGENT_TIMEOUT_SECONDS")
    
    # Medical Coding
    ICD10_DATABASE_PATH: str = Field(default="./data/icd10.db", env="ICD10_DATABASE_PATH")
    CPT_DATABASE_PATH: str = Field(default="./data/cpt.db", env="CPT_DATABASE_PATH")
    HCPCS_DATABASE_PATH: str = Field(default="./data/hcpcs.db", env="HCPCS_DATABASE_PATH")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# HIPAA Compliance Configuration
HIPAA_REQUIRED_FIELDS = [
    "patient_id",
    "medical_record_number",
    "social_security_number",
    "date_of_birth",
    "diagnosis_codes",
    "procedure_codes",
    "physician_notes",
    "insurance_information"
]

# Audit Event Types
AUDIT_EVENT_TYPES = {
    "DATA_ACCESS": "Data Access",
    "DATA_MODIFICATION": "Data Modification",
    "DATA_DELETION": "Data Deletion",
    "LOGIN_SUCCESS": "Login Success",
    "LOGIN_FAILURE": "Login Failure",
    "LOGOUT": "Logout",
    "CLAIM_SUBMISSION": "Claim Submission",
    "CLAIM_DENIAL": "Claim Denial",
    "PAYMENT_PROCESSING": "Payment Processing",
    "DOCUMENT_UPLOAD": "Document Upload",
    "DOCUMENT_DOWNLOAD": "Document Download",
    "AGENT_EXECUTION": "Agent Execution",
    "SYSTEM_ERROR": "System Error"
}

# Medical Code Types
MEDICAL_CODE_TYPES = {
    "ICD10CM": "ICD-10-CM Diagnosis Codes",
    "ICD10PCS": "ICD-10-PCS Procedure Codes",
    "CPT": "Current Procedural Terminology",
    "HCPCS": "Healthcare Common Procedure Coding System",
    "NDC": "National Drug Code",
    "LOINC": "Logical Observation Identifiers Names and Codes",
    "SNOMED": "Systematized Nomenclature of Medicine Clinical Terms"
}

# Claim Status Types
CLAIM_STATUS_TYPES = {
    "DRAFT": "Draft",
    "SUBMITTED": "Submitted",
    "ACCEPTED": "Accepted",
    "REJECTED": "Rejected",
    "DENIED": "Denied",
    "PAID": "Paid",
    "PARTIALLY_PAID": "Partially Paid",
    "APPEALED": "Appealed",
    "CLOSED": "Closed"
}

# Agent Types
AGENT_TYPES = {
    "REGISTRATION": "Patient Registration and Insurance Verification",
    "CODING": "Medical Coding",
    "SUBMISSION": "Claim Submission",
    "FOLLOWUP": "Claim Follow-up and Denial Management",
    "BILLING": "Patient Billing and Collections",
    "REPORTING": "Financial Reporting and Analysis",
    "RECORDS": "Patient Records and Data Integrity",
    "COMMUNICATION": "Communication and Collaboration"
} 