"""
Communication Agent - CrewAI Implementation

This agent specializes in patient communications, team collaboration,
and multi-channel communication management with automated workflows.
"""

from crewai import Agent, Task
from typing import Dict, Any, List

from app.agents.base import MedicalBillingAgent, MedicalBillingCrew
from app.tools import (
    PatientCommunicationTool,
    TeamCollaborationTool,
    PatientLookupTool,
    ClaimLookupTool,
    StatementGenerationTool
)
from app.utils.logging import get_logger

logger = get_logger("agents.communication")


def create_communication_agent() -> Agent:
    """Create Communication Agent using CrewAI framework"""
    
    # Initialize tools for communication
    tools = [
        PatientCommunicationTool(),
        TeamCollaborationTool(),
        PatientLookupTool(),
        ClaimLookupTool(),
        StatementGenerationTool()
    ]
    
    agent = MedicalBillingAgent(
        role="Communication Specialist",
        goal=(
            "Facilitate effective communications between patients, providers, and staff "
            "through multiple channels, coordinate team collaboration, and ensure "
            "timely, accurate, and HIPAA-compliant information exchange across "
            "all stakeholders in the healthcare billing process."
        ),
        backstory=(
            "You are an expert in healthcare communications with deep knowledge of "
            "patient engagement strategies, HIPAA compliance, and multi-channel "
            "communication management. You have extensive experience in automated "
            "messaging systems, customer service protocols, and team coordination. "
            "Your expertise includes chatbot management, escalation procedures, "
            "and communication analytics. You work to ensure all stakeholders "
            "receive timely, relevant, and appropriately formatted communications "
            "while maintaining privacy and regulatory compliance."
        ),
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=3,
        allow_delegation=True
    )
    
    return agent


class CommunicationTasks:
    """Pre-defined tasks for Communication Agent"""
    
    @staticmethod
    def manage_patient_communications(comm_data: Dict[str, Any]) -> Task:
        """Task to manage patient communications across multiple channels"""
        
        comm_json = str(comm_data)
        
        return Task(
            description=f"""
            Manage patient communications across multiple channels for the following:
            
            {comm_json}
            
            Communication management requirements:
            1. Route communications to appropriate channels (email, SMS, mail, portal)
            2. Personalize messages based on patient preferences and history
            3. Schedule and automate recurring communications
            4. Track delivery status and engagement metrics
            5. Handle patient responses and inquiries
            6. Escalate complex issues to appropriate staff
            7. Ensure HIPAA compliance and privacy protection
            
            Use PatientCommunicationTool for multi-channel messaging.
            Use PatientLookupTool to verify patient preferences and contact information.
            """,
            expected_output=(
                "Patient communication management report with message delivery status, "
                "engagement metrics, response handling, escalations, and compliance "
                "documentation formatted as structured JSON with tracking information."
            ),
            agent=None
        )
    
    @staticmethod
    def coordinate_team_workflows(workflow_data: Dict[str, Any]) -> Task:
        """Task to coordinate team workflows and internal communications"""
        
        workflow_json = str(workflow_data)
        
        return Task(
            description=f"""
            Coordinate team workflows and internal communications for the following:
            
            {workflow_json}
            
            Team coordination requirements:
            1. Facilitate cross-departmental communication and collaboration
            2. Manage task assignments and workflow escalations
            3. Coordinate case reviews and consultation requests
            4. Share knowledge and best practices across teams
            5. Track workflow progress and bottlenecks
            6. Generate team performance and communication metrics
            7. Ensure timely resolution of patient-related issues
            
            Use TeamCollaborationTool for workflow coordination.
            Use ClaimLookupTool to provide context for case discussions.
            """,
            expected_output=(
                "Team workflow coordination report with task assignments, progress tracking, "
                "escalation handling, collaboration metrics, and resolution outcomes "
                "formatted as structured JSON with workflow analytics."
            ),
            agent=None
        )
    
    @staticmethod
    def handle_patient_inquiries(inquiry_data: Dict[str, Any]) -> Task:
        """Task to handle patient inquiries and support requests"""
        
        inquiry_json = str(inquiry_data)
        
        return Task(
            description=f"""
            Handle patient inquiries and support requests for the following:
            
            {inquiry_json}
            
            Inquiry handling requirements:
            1. Categorize and prioritize incoming patient inquiries
            2. Provide automated responses for common questions
            3. Route complex inquiries to appropriate specialists
            4. Maintain comprehensive inquiry tracking and follow-up
            5. Generate patient satisfaction surveys and feedback collection
            6. Document all interactions for quality assurance
            7. Identify trends and opportunities for process improvement
            
            Use PatientCommunicationTool for inquiry responses.
            Use PatientLookupTool and ClaimLookupTool for context research.
            Use TeamCollaborationTool for specialist routing.
            """,
            expected_output=(
                "Patient inquiry handling report with categorized inquiries, response times, "
                "resolution rates, satisfaction scores, and improvement recommendations "
                "formatted as structured JSON with service metrics."
            ),
            agent=None
        )
    
    @staticmethod
    def implement_chatbot_services(chatbot_data: Dict[str, Any]) -> Task:
        """Task to implement and manage chatbot services"""
        
        chatbot_json = str(chatbot_data)
        
        return Task(
            description=f"""
            Implement and manage chatbot services for the following scenarios:
            
            {chatbot_json}
            
            Chatbot implementation requirements:
            1. Design conversational flows for common patient interactions
            2. Implement natural language processing for intent recognition
            3. Integrate with patient records for personalized responses
            4. Provide seamless handoff to human agents when needed
            5. Monitor chatbot performance and optimization opportunities
            6. Ensure HIPAA compliance in automated interactions
            7. Generate analytics on chatbot usage and effectiveness
            
            Use PatientCommunicationTool for automated interactions.
            Use PatientLookupTool for personalized response generation.
            Use TeamCollaborationTool for human agent handoffs.
            """,
            expected_output=(
                "Chatbot implementation report with conversation flows, performance metrics, "
                "handoff procedures, compliance measures, and optimization recommendations "
                "formatted as structured JSON with chatbot analytics."
            ),
            agent=None
        )
    
    @staticmethod
    def generate_communication_analytics(analytics_data: Dict[str, Any]) -> Task:
        """Task to generate communication analytics and insights"""
        
        analytics_json = str(analytics_data)
        
        return Task(
            description=f"""
            Generate communication analytics and insights from the following data:
            
            {analytics_json}
            
            Communication analytics requirements:
            1. Analyze communication volume and channel preferences
            2. Measure response times and resolution rates
            3. Track patient satisfaction and engagement metrics
            4. Identify communication bottlenecks and inefficiencies
            5. Generate insights on optimal communication timing
            6. Benchmark performance against industry standards
            7. Provide recommendations for communication strategy optimization
            
            Use PatientCommunicationTool for communication data analysis.
            Use TeamCollaborationTool for internal communication metrics.
            """,
            expected_output=(
                "Communication analytics report with volume analysis, performance metrics, "
                "satisfaction trends, optimization opportunities, and strategic recommendations "
                "formatted as structured JSON with analytical insights."
            ),
            agent=None
        )


def create_communication_crew(comm_data: Dict[str, Any]) -> MedicalBillingCrew:
    """Create a crew for comprehensive communication workflow"""
    
    # Create the communication agent
    comm_agent = create_communication_agent()
    
    # Create tasks for the communication workflow
    tasks = [
        CommunicationTasks.manage_patient_communications(comm_data),
        CommunicationTasks.coordinate_team_workflows(comm_data.get("workflow_data", {})),
        CommunicationTasks.handle_patient_inquiries(comm_data.get("inquiry_data", {})),
        CommunicationTasks.generate_communication_analytics(comm_data.get("analytics_data", {}))
    ]
    
    # Assign agent to tasks
    for task in tasks:
        task.agent = comm_agent
    
    # Create crew
    crew = MedicalBillingCrew(
        agents=[comm_agent],
        tasks=tasks,
        verbose=True,
        memory=True,
        process="sequential"
    )
    
    return crew


# Example usage function for testing
async def process_communications(comm_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process communication workflow"""
    
    try:
        # Create communication crew
        crew = create_communication_crew(comm_data)
        
        # Execute communication workflow
        result = crew.kickoff()
        
        logger.info(f"Communication processing completed for period {comm_data.get('period', 'unknown')}")
        
        return {
            "status": "success",
            "period": comm_data.get("period"),
            "communication_result": result,
            "processed_at": comm_data.get("processed_at")
        }
        
    except Exception as e:
        error_msg = f"Communication processing failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "period": comm_data.get("period"),
            "error": error_msg
        } 