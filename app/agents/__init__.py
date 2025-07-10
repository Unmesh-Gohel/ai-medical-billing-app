"""
AI Agents for Medical Billing Application - CrewAI Framework

This package contains 8 specialized CrewAI agents:
1. Patient Registration and Insurance Verification Agent
2. Medical Coding Agent  
3. Claim Submission Agent
4. Denial Management Agent
5. Patient Billing and Collections Agent
6. Financial Reporting and Analysis Agent
7. Data Integrity Agent
8. Communication and Collaboration Agent
"""

# CrewAI agent creation functions
from .registration import create_patient_registration_agent, create_patient_registration_crew
from .medical_coding import create_medical_coding_agent, create_medical_coding_crew
from .claim_submission import create_claim_submission_agent, create_claim_submission_crew
from .denial_management import create_denial_management_agent, create_denial_management_crew
from .patient_billing import create_patient_billing_agent, create_patient_billing_crew
from .financial_reporting import create_financial_reporting_agent, create_financial_reporting_crew
from .data_integrity import create_data_integrity_agent, create_data_integrity_crew
from .communication import create_communication_agent, create_communication_crew

# Base CrewAI framework components
from .base import MedicalBillingAgent, MedicalBillingCrew

# Legacy agent classes for backward compatibility (if needed)
# Note: These are imported from the updated base module
from .base import BaseAgent, AgentResult, AgentError

# Legacy orchestrator components for backward compatibility
from .base import AgentOrchestrator, AgentTask, TaskPriority

__all__ = [
    # CrewAI agent creation functions
    "create_patient_registration_agent",
    "create_patient_registration_crew", 
    "create_medical_coding_agent",
    "create_medical_coding_crew",
    "create_claim_submission_agent", 
    "create_claim_submission_crew",
    "create_denial_management_agent",
    "create_denial_management_crew",
    "create_patient_billing_agent",
    "create_patient_billing_crew",
    "create_financial_reporting_agent",
    "create_financial_reporting_crew",
    "create_data_integrity_agent",
    "create_data_integrity_crew",
    "create_communication_agent", 
    "create_communication_crew",
    
    # Base CrewAI components
    "MedicalBillingAgent",
    "MedicalBillingCrew",
    
    # Legacy components for backward compatibility
    "BaseAgent",
    "AgentResult", 
    "AgentError",
    "AgentOrchestrator",
    "AgentTask",
    "TaskPriority"
] 