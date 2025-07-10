"""
Patient Registration and Insurance Verification Agent - CrewAI Implementation
"""

from typing import List, Any
from crewai import Agent

from app.agents.base import MedicalBillingCrew, AgentRole
from app.tools.ocr_tools import OCRTool, InsuranceCardTool
from app.tools.eligibility_tools import EligibilityCheckTool, CoverageVerificationTool
from app.tools.database_tools import PatientLookupTool, InsuranceLookupTool
from app.utils.logging import get_logger


logger = get_logger("agents.registration")


def create_patient_registration_agent(crew: MedicalBillingCrew) -> Any:
    """Create and configure the Patient Registration Agent using CrewAI"""
    
    # Define the tools this agent will use
    tools = [
        OCRTool(),
        InsuranceCardTool(), 
        EligibilityCheckTool(),
        CoverageVerificationTool(),
        PatientLookupTool(),
        InsuranceLookupTool()
    ]
    
    # Define the agent's role, goal, and backstory
    role = AgentRole.REGISTRATION
    goal = """Process patient intake forms, verify insurance eligibility, and register patients 
    in the medical billing system with accuracy and HIPAA compliance."""
    
    backstory = """You are an expert Patient Registration Specialist with over 10 years of experience
    in medical billing and patient intake processes. You have extensive knowledge of:
    
    - OCR processing for patient forms and insurance cards
    - Real-time insurance eligibility verification
    - HIPAA compliance and patient data protection
    - Medical insurance plans and benefit structures
    - Patient registration workflows and documentation requirements
    
    Your expertise ensures accurate patient data capture, proper insurance verification,
    and seamless integration with electronic health record systems. You always prioritize
    patient privacy and data accuracy while maintaining efficient processing workflows."""
    
    # Create the agent using the crew framework
    agent = crew.create_agent(
        agent_id="patient_registration_agent",
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools
    )
    
    logger.info("Patient Registration Agent created with CrewAI framework")
    return agent


class PatientRegistrationTasks:
    """Predefined tasks for the Patient Registration Agent"""
    
    @staticmethod
    def process_intake_form_task(document_path: str) -> str:
        """Task for processing patient intake forms"""
        return f"""
        Process the patient intake form located at: {document_path}
        
        Please perform the following steps:
        1. Use OCR to extract text from the intake form
        2. Extract and structure patient demographic information including:
           - Full name, date of birth, gender
           - Contact information (phone, email, address)
           - Emergency contact details
           - Medical history and current medications
        3. Validate the extracted data for completeness and accuracy
        4. Flag any missing or unclear information that requires follow-up
        5. Return structured patient data ready for registration
        
        Ensure all processing follows HIPAA compliance guidelines.
        """
    
    @staticmethod
    def process_insurance_card_task(front_image_path: str, back_image_path: str = None) -> str:
        """Task for processing insurance cards"""
        return f"""
        Process the insurance card images to extract insurance information:
        - Front image: {front_image_path}
        {"- Back image: " + back_image_path if back_image_path else ""}
        
        Please perform the following steps:
        1. Use OCR to extract text from both sides of the insurance card
        2. Extract key insurance information including:
           - Insurance company name and contact information
           - Member ID and group number
           - Plan type and effective dates
           - Copay, deductible, and benefit information
           - Provider network details
        3. Validate the insurance information format and completeness
        4. Return structured insurance data for eligibility verification
        
        Focus on accuracy as this information is critical for claim processing.
        """
    
    @staticmethod  
    def verify_eligibility_task(patient_info: dict, insurance_info: dict) -> str:
        """Task for verifying insurance eligibility"""
        return f"""
        Verify insurance eligibility for the patient using the following information:
        
        Patient Information: {patient_info}
        Insurance Information: {insurance_info}
        
        Please perform the following steps:
        1. Use the eligibility verification tool to check current coverage status
        2. Verify coverage for the planned service date
        3. Check benefit details including:
           - Deductible amounts and remaining balances
           - Copay requirements for different service types
           - Out-of-pocket maximums
           - Prior authorization requirements
        4. Document any coverage limitations or restrictions
        5. Provide clear eligibility status and recommendations
        
        Return comprehensive eligibility information for the billing team.
        """
    
    @staticmethod
    def register_patient_task(patient_data: dict, insurance_data: dict, eligibility_data: dict) -> str:
        """Task for registering a new patient"""
        return f"""
        Register a new patient in the medical billing system using the validated information:
        
        Patient Data: {patient_data}
        Insurance Data: {insurance_data}
        Eligibility Data: {eligibility_data}
        
        Please perform the following steps:
        1. Check if the patient already exists in the system
        2. If new patient, create comprehensive patient record including:
           - Demographics and contact information
           - Insurance details and coverage information
           - Emergency contacts and preferences
        3. If existing patient, update any changed information
        4. Link insurance eligibility verification results
        5. Set up billing preferences and communication methods
        6. Generate patient ID and confirm successful registration
        
        Ensure all data entry follows proper validation and HIPAA compliance.
        """
    
    @staticmethod
    def update_patient_info_task(patient_id: str, updated_info: dict) -> str:
        """Task for updating existing patient information"""
        return f"""
        Update patient information for Patient ID: {patient_id}
        
        Updated Information: {updated_info}
        
        Please perform the following steps:
        1. Look up the existing patient record
        2. Validate the updated information for accuracy and completeness
        3. Compare with existing data to identify changes
        4. Update the patient record with new information
        5. Maintain audit trail of changes for compliance
        6. Verify insurance information if insurance details changed
        7. Confirm successful update and provide summary of changes
        
        Ensure all updates maintain data integrity and HIPAA compliance.
        """ 