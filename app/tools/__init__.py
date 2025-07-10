"""
Custom tools for CrewAI agents in the Medical Billing System
"""

from .ocr_tools import OCRTool, InsuranceCardTool
from .eligibility_tools import EligibilityCheckTool, CoverageVerificationTool
from .coding_tools import MedicalCodingTool, DiagnosisLookupTool, ProcedureLookupTool
from .claim_tools import ClaimGenerationTool, ClaimSubmissionTool, ClaimStatusTool
from .denial_tools import DenialAnalysisTool, AppealGenerationTool
# Billing and Payment Tools
from .billing_tools import (
    StatementGenerationTool,
    PaymentProcessingTool
)

# Reporting and Analytics Tools  
from .reporting_tools import (
    FinancialReportTool,
    PerformanceAnalyticsTool
)

# Communication and Collaboration Tools
from .communication_tools import (
    PatientCommunicationTool,
    TeamCollaborationTool
)
from .fhir_tools import FHIRPatientTool, FHIREncounterTool
from .database_tools import PatientLookupTool, ClaimLookupTool, InsuranceLookupTool

__all__ = [
    # OCR Tools
    "OCRTool",
    "InsuranceCardTool",
    
    # Eligibility Tools
    "EligibilityCheckTool", 
    "CoverageVerificationTool",
    
    # Medical Coding Tools
    "MedicalCodingTool",
    "DiagnosisLookupTool",
    "ProcedureLookupTool",
    
    # Claim Tools
    "ClaimGenerationTool",
    "ClaimSubmissionTool", 
    "ClaimStatusTool",
    
    # Denial Management Tools
    "DenialAnalysisTool",
    "AppealGenerationTool",
    
    # Database Tools
    "PatientLookupTool",
    "ClaimLookupTool",
    "InsuranceLookupTool",
    
    # Billing Tools
    "StatementGenerationTool",
    "PaymentProcessingTool",
    
    # Reporting Tools
    "FinancialReportTool",
    "PerformanceAnalyticsTool",
    
    # Communication Tools
    "PatientCommunicationTool",
    "TeamCollaborationTool"
] 