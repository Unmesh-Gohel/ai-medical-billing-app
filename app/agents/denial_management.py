"""
Denial Management Agent - CrewAI Implementation

This agent specializes in claim follow-up, denial analysis, and automated
appeal generation with pattern recognition and root cause analysis.
"""

from crewai import Agent, Task
from typing import Dict, Any, List

from app.agents.base import MedicalBillingAgent, MedicalBillingCrew
from app.tools import (
    DenialAnalysisTool,
    AppealGenerationTool,
    ClaimStatusTool,
    ClaimLookupTool,
    PatientCommunicationTool,
    TeamCollaborationTool
)
from app.utils.logging import get_logger

logger = get_logger("agents.denial_management")


def create_denial_management_agent() -> Agent:
    """Create Denial Management Agent using CrewAI framework"""
    
    # Initialize tools for denial management
    tools = [
        DenialAnalysisTool(),
        AppealGenerationTool(),
        ClaimStatusTool(),
        ClaimLookupTool(),
        PatientCommunicationTool(),
        TeamCollaborationTool()
    ]
    
    agent = MedicalBillingAgent(
        role="Denial Management Specialist",
        goal=(
            "Monitor claim denials, analyze denial patterns, generate compelling appeals "
            "with supporting documentation, and implement systematic process improvements "
            "to reduce future denials and maximize reimbursement recovery."
        ),
        backstory=(
            "You are an expert in denial management with deep knowledge of payer policies, "
            "appeal regulations, and healthcare reimbursement rules. You have extensive "
            "experience in pattern analysis, root cause identification, and systematic "
            "process improvement. Your expertise includes automated monitoring systems, "
            "appeal letter generation, and evidence compilation. You work collaboratively "
            "with clinical staff to gather supporting documentation and educate teams "
            "on denial prevention strategies."
        ),
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=3,
        allow_delegation=True
    )
    
    return agent


class DenialManagementTasks:
    """Pre-defined tasks for Denial Management Agent"""
    
    @staticmethod
    def monitor_claim_denials(monitoring_data: Dict[str, Any]) -> Task:
        """Task to monitor and identify new claim denials"""
        
        monitoring_json = str(monitoring_data)
        
        return Task(
            description=f"""
            Monitor and identify new claim denials from the following data sources:
            
            {monitoring_json}
            
            Monitoring requirements:
            1. Scan electronic remittance advice (835) files for denied claims
            2. Identify patterns in denial reasons and payer behavior
            3. Categorize denials by type, urgency, and appeal potential
            4. Track denial rates by provider, payer, and service type
            5. Flag high-value denials requiring immediate attention
            6. Generate automated alerts for critical denials
            7. Update denial tracking dashboard with real-time data
            
            Use ClaimStatusTool to check current claim positions.
            Use DenialAnalysisTool to categorize and prioritize denials.
            """,
            expected_output=(
                "Comprehensive denial monitoring report with new denials identified, "
                "categorized by priority and type, trend analysis, and immediate action "
                "items formatted as structured JSON with alert notifications."
            ),
            agent=None
        )
    
    @staticmethod
    def analyze_denial_patterns(denial_data: Dict[str, Any]) -> Task:
        """Task to analyze denial patterns and identify root causes"""
        
        denial_json = str(denial_data)
        
        return Task(
            description=f"""
            Analyze denial patterns and identify root causes from the following data:
            
            {denial_json}
            
            Analysis requirements:
            1. Identify common denial reasons and error patterns
            2. Analyze denial trends by payer, provider, and service type
            3. Calculate financial impact of denial categories
            4. Identify systemic issues requiring process improvements
            5. Benchmark denial rates against industry standards
            6. Generate predictive insights for future denial prevention
            7. Create actionable recommendations for staff training
            
            Use DenialAnalysisTool for pattern recognition and trend analysis.
            Use ClaimLookupTool to gather supporting claim details.
            """,
            expected_output=(
                "Detailed pattern analysis report with root cause identification, "
                "financial impact assessment, prevention recommendations, and process "
                "improvement opportunities formatted as structured JSON with visualizations."
            ),
            agent=None
        )
    
    @staticmethod
    def generate_appeals(appeal_data: Dict[str, Any]) -> Task:
        """Task to generate compelling appeal letters and documentation"""
        
        appeal_json = str(appeal_data)
        
        return Task(
            description=f"""
            Generate compelling appeal letters and compile supporting documentation:
            
            {appeal_json}
            
            Appeal generation requirements:
            1. Create customized appeal letters for each denial reason
            2. Compile relevant medical records and supporting documentation
            3. Reference applicable payer policies and coverage guidelines
            4. Include medical necessity justifications when appropriate
            5. Apply proper appeal formatting and submission requirements
            6. Generate tracking numbers and follow-up schedules
            7. Ensure compliance with appeal deadlines and procedures
            
            Use AppealGenerationTool to create professional appeal documents.
            Use TeamCollaborationTool to coordinate with clinical staff for documentation.
            """,
            expected_output=(
                "Complete appeal package with customized letters, supporting documentation, "
                "submission instructions, tracking information, and follow-up schedule "
                "formatted as structured JSON with embedded document references."
            ),
            agent=None
        )
    
    @staticmethod
    def track_appeal_outcomes(tracking_data: Dict[str, Any]) -> Task:
        """Task to track appeal submissions and outcomes"""
        
        tracking_json = str(tracking_data)
        
        return Task(
            description=f"""
            Track appeal submissions and monitor outcomes for the following appeals:
            
            {tracking_json}
            
            Tracking requirements:
            1. Monitor appeal status through payer portals and communications
            2. Process appeal responses and payment decisions
            3. Calculate appeal success rates by denial reason and payer
            4. Identify appeals requiring additional levels of review
            5. Generate resubmission workflows for successful appeals
            6. Update financial projections based on appeal outcomes
            7. Document lessons learned for future appeal strategies
            
            Use ClaimStatusTool to monitor appeal progress.
            Use DenialAnalysisTool to update success rate metrics.
            """,
            expected_output=(
                "Comprehensive appeal tracking report with current status, success rates, "
                "financial recovery amounts, pending actions, and strategic insights "
                "formatted as structured JSON with performance metrics."
            ),
            agent=None
        )
    
    @staticmethod
    def implement_prevention_strategies(prevention_data: Dict[str, Any]) -> Task:
        """Task to implement denial prevention strategies"""
        
        prevention_json = str(prevention_data)
        
        return Task(
            description=f"""
            Implement denial prevention strategies based on analysis insights:
            
            {prevention_json}
            
            Prevention implementation requirements:
            1. Develop targeted training programs for common denial reasons
            2. Create automated validation rules for high-risk claim types
            3. Implement real-time alerts for potential denial triggers
            4. Establish provider education initiatives on documentation requirements
            5. Design workflow improvements to address systematic issues
            6. Create monitoring dashboards for prevention effectiveness
            7. Coordinate with IT to implement system enhancements
            
            Use TeamCollaborationTool to coordinate implementation across departments.
            Use PatientCommunicationTool to engage patients in prevention efforts.
            """,
            expected_output=(
                "Prevention strategy implementation plan with specific initiatives, "
                "timeline, responsible parties, success metrics, and monitoring "
                "procedures formatted as structured JSON with implementation tracking."
            ),
            agent=None
        )


def create_denial_management_crew(denial_data: Dict[str, Any]) -> MedicalBillingCrew:
    """Create a crew for comprehensive denial management workflow"""
    
    # Create the denial management agent
    denial_agent = create_denial_management_agent()
    
    # Create tasks for the denial management workflow
    tasks = [
        DenialManagementTasks.monitor_claim_denials(denial_data),
        DenialManagementTasks.analyze_denial_patterns(denial_data.get("historical_data", {})),
        DenialManagementTasks.generate_appeals(denial_data.get("appeals_needed", {})),
        DenialManagementTasks.track_appeal_outcomes(denial_data.get("pending_appeals", {}))
    ]
    
    # Assign agent to tasks
    for task in tasks:
        task.agent = denial_agent
    
    # Create crew
    crew = MedicalBillingCrew(
        agents=[denial_agent],
        tasks=tasks,
        verbose=True,
        memory=True,
        process="sequential"
    )
    
    return crew


# Example usage function for testing
async def process_denial_management(denial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process denial management workflow"""
    
    try:
        # Create denial management crew
        crew = create_denial_management_crew(denial_data)
        
        # Execute denial management workflow
        result = crew.kickoff()
        
        logger.info(f"Denial management completed for period {denial_data.get('period', 'unknown')}")
        
        return {
            "status": "success",
            "period": denial_data.get("period"),
            "denial_management_result": result,
            "processed_at": denial_data.get("processed_at")
        }
        
    except Exception as e:
        error_msg = f"Denial management failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "period": denial_data.get("period"),
            "error": error_msg
        } 