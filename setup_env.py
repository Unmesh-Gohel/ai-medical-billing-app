#!/usr/bin/env python3
"""
Setup script for AI Medical Billing System environment variables
"""

import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create a .env file with default values"""
    env_content = f"""# AI Medical Billing System Environment Variables
# Generated on {os.getcwd()}

# Application Settings
DEBUG=true
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000

# Database Configuration (Update these for your database)
DATABASE_URL=sqlite:///./medical_billing.db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis Configuration (Update for your Redis instance)
REDIS_URL=redis://localhost:6379

# Security Keys
SECRET_KEY={generate_secret_key()}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENCRYPTION_KEY={generate_secret_key()}

# AI/ML Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Vector Database
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Compliance and Audit
AUDIT_LOG_RETENTION_DAYS=2555
HIPAA_COMPLIANCE_MODE=true

# Agent Configuration
MAX_CONCURRENT_AGENTS=10
AGENT_TIMEOUT_SECONDS=300

# Medical Coding Databases
ICD10_DATABASE_PATH=./data/icd10.db
CPT_DATABASE_PATH=./data/cpt.db
HCPCS_DATABASE_PATH=./data/hcpcs.db
"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists. Backing up to .env.backup")
        env_file.rename(".env.backup")
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file with default values")
    print("📝 Please update the following values in .env:")
    print("   - DATABASE_URL (if using PostgreSQL/MySQL)")
    print("   - REDIS_URL (if using Redis)")
    print("   - OPENAI_API_KEY (required for AI features)")
    print("   - Other API keys as needed")

if __name__ == "__main__":
    print("🏥 Setting up AI Medical Billing System environment...")
    create_env_file()
    print("✅ Setup complete! You can now run: python run_server.py") 