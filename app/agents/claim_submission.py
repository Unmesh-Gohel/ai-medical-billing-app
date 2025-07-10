"""
Claim Submission Agent - CrewAI Implementation

This agent specializes in electronic claim submission, validation, and tracking
with real-time clearinghouse integration and error detection.
"""

from crewai import Agent, Task
from typing import Dict, Any, List

from app.agents.base import MedicalBillingAgent, MedicalBillingCrew
from app.tools import (
    ClaimGenerationTool,
    ClaimSubmissionTool,
    ClaimStatusTool,
    EligibilityCheckTool,
    PatientLookupTool,
    TeamCollaborationTool
)
from app.utils.logging import get_logger

logger = get_logger("agents.claim_submission")


def create_claim_submission_agent() -> Agent:
    """Create Claim Submission Agent using CrewAI framework"""
    
    # Initialize tools for claim submission
    tools = [
        ClaimGenerationTool(),
        ClaimSubmissionTool(),
        ClaimStatusTool(),
        EligibilityCheckTool(),
        PatientLookupTool(),
        TeamCollaborationTool()
    ]
    
    agent = MedicalBillingAgent(
        role="Claim Submission Specialist",
        goal=(
            "Generate clean claims, validate all required fields and attachments, "
            "submit claims electronically to payers, and track submission status "
            "to ensure timely reimbursement and minimize denials."
        ),
        backstory=(
            "You are an expert in electronic claim submission with deep knowledge of "
            "X12 EDI standards, HIPAA compliance, and payer-specific requirements. "
            "You have extensive experience with clearinghouses, real-time adjudication, "
            "and claim validation rules. Your expertise includes pre-submission scrubbing, "
            "attachment handling, and automated resubmission workflows. You work closely "
            "with coding staff to ensure claim accuracy and collaborate with payers to "
            "resolve submission issues quickly."
        ),
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=3,
        allow_delegation=True
    )
    
    return agent


class ClaimSubmissionTasks:
    """Pre-defined tasks for Claim Submission Agent"""
    
    @staticmethod
    def validate_claim_data(claim_data: Dict[str, Any]) -> Task:
        """Task to validate claim data before submission"""
        
        claim_json = str(claim_data)
        
        return Task(
            description=f"""
            Validate the following claim data for completeness and accuracy before submission:
            
            {claim_json}
            
            Validation requirements:
            1. Verify all required fields are present and properly formatted
            2. Validate patient demographics and insurance information
            3. Check diagnosis and procedure code compatibility
            4. Verify provider credentials and NPI numbers
            5. Validate dates of service and authorization numbers
            6. Check for duplicate claim submissions
            7. Ensure compliance with payer-specific requirements
            
            Use EligibilityCheckTool to verify current insurance coverage.
            Use PatientLookupTool to confirm patient information accuracy.
            """,
            expected_output=(
                "Comprehensive validation report with pass/fail status for each validation rule, "
                "identified errors or warnings, specific remediation steps, and claim readiness "
                "assessment formatted as structured JSON."
            ),
            agent=None
        )
    
    @staticmethod
    def generate_clean_claim(validated_data: Dict[str, Any]) -> Task:
        """Task to generate a clean, submission-ready claim"""
        
        data_json = str(validated_data)
        
        return Task(
            description=f"""
            Generate a clean, submission-ready claim from the validated data:
            
            {data_json}
            
            Generation requirements:
            1. Create properly formatted ANSI X12 837 claim file
            2. Apply payer-specific formatting and field requirements
            3. Include all required loops and segments
            4. Generate appropriate claim control numbers
            5. Apply correct place of service and type of bill codes
            6. Include supporting documentation references
            7. Ensure HIPAA compliance and data security
            
            Use ClaimGenerationTool to create the electronic claim format.
            """,
            expected_output=(
                "Complete electronic claim in X12 837 format with all required segments, "
                "control numbers, validation summary, and submission instructions "
                "formatted as structured JSON with embedded claim data."
            ),
            agent=None
        )
    
    @staticmethod
    def submit_electronic_claim(claim_data: Dict[str, Any]) -> Task:
        """Task to submit claim electronically to clearinghouse"""
        
        claim_json = str(claim_data)
        
        return Task(
            description=f"""
            Submit the following electronic claim to the appropriate clearinghouse:
            
            {claim_json}
            
            Submission requirements:
            1. Route claim to correct clearinghouse or payer
            2. Apply appropriate transmission protocols (HTTPS, SFTP, etc.)
            3. Generate submission confirmation and tracking numbers
            4. Set up automated status checking schedules
            5. Handle real-time adjudication responses when available
            6. Log all transmission details for audit purposes
            7. Trigger follow-up workflows based on acknowledgments
            
            Use ClaimSubmissionTool for electronic transmission.
            Use ClaimStatusTool to verify successful receipt.
            """,
            expected_output=(
                "Submission confirmation with tracking numbers, transmission details, "
                "acknowledgment status, estimated processing timeline, and next steps "
                "for status monitoring formatted as structured JSON."
            ),
            agent=None
        )
    
    @staticmethod
    def track_claim_status(tracking_data: Dict[str, Any]) -> Task:
        """Task to track claim status and handle responses"""
        
        tracking_json = str(tracking_data)
        
        return Task(
            description=f"""
            Track claim status and process payer responses for the following submissions:
            
            {tracking_json}
            
            Tracking requirements:
            1. Monitor claim status through clearinghouse portals
            2. Process acknowledgment and rejection reports (997/999)
            3. Handle payer adjudication responses (835/277CA)
            4. Identify and categorize claim denials or rejections
            5. Generate resubmission workflows for correctable errors
            6. Escalate complex issues to appropriate staff
            7. Update claim status in billing system
            
            Use ClaimStatusTool for status monitoring and response processing.
            Use TeamCollaborationTool for issue escalation when needed.
            """,
            expected_output=(
                "Comprehensive status report with current claim positions, payer responses, "
                "identified issues requiring action, resubmission recommendations, and "
                "escalation items formatted as structured JSON with action priorities."
            ),
            agent=None
        )
    
    @staticmethod
    def handle_claim_rejections(rejection_data: Dict[str, Any]) -> Task:
        """Task to analyze and resolve claim rejections"""
        
        rejection_json = str(rejection_data)
        
        return Task(
            description=f"""
            Analyze and resolve the following claim rejections:
            
            {rejection_json}
            
            Resolution requirements:
            1. Categorize rejection reasons and error codes
            2. Identify root causes and correction strategies
            3. Prioritize rejections by financial impact and urgency
            4. Generate corrected claim data for resubmission
            5. Implement process improvements to prevent recurrence
            6. Coordinate with clinical staff for documentation issues
            7. Track rejection resolution metrics and trends
            
            Use ClaimGenerationTool to create corrected claims.
            Use TeamCollaborationTool to coordinate with other departments.
            """,
            expected_output=(
                "Rejection analysis report with categorized errors, correction actions taken, "
                "resubmission timeline, process improvement recommendations, and performance "
                "metrics formatted as structured JSON with resolution tracking."
            ),
            agent=None
        )


def create_claim_submission_crew(claim_data: Dict[str, Any]) -> MedicalBillingCrew:
    """Create a crew for comprehensive claim submission workflow"""
    
    # Create the submission agent
    submission_agent = create_claim_submission_agent()
    
    # Create tasks for the submission workflow
    tasks = [
        ClaimSubmissionTasks.validate_claim_data(claim_data),
        ClaimSubmissionTasks.generate_clean_claim(claim_data),
        ClaimSubmissionTasks.submit_electronic_claim(claim_data),
        ClaimSubmissionTasks.track_claim_status(claim_data.get("tracking_info", {}))
    ]
    
    # Assign agent to tasks
    for task in tasks:
        task.agent = submission_agent
    
    # Create crew
    crew = MedicalBillingCrew(
        agents=[submission_agent],
        tasks=tasks,
        verbose=True,
        memory=True,
        process="sequential"
    )
    
    return crew


# Example usage function for testing
async def process_claim_submission(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process claim submission workflow"""
    
    try:
        # Create submission crew
        crew = create_claim_submission_crew(claim_data)
        
        # Execute submission workflow
        result = crew.kickoff()
        
        logger.info(f"Claim submission completed for claim {claim_data.get('claim_id', 'unknown')}")
        
        return {
            "status": "success",
            "claim_id": claim_data.get("claim_id"),
            "submission_result": result,
            "processed_at": claim_data.get("processed_at")
        }
        
    except Exception as e:
        error_msg = f"Claim submission failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "claim_id": claim_data.get("claim_id"),
            "error": error_msg
        } 