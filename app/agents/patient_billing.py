"""
Patient Billing Agent - CrewAI Implementation

This agent specializes in patient billing, statement generation, payment processing,
and collections management with automated workflows and patient communication.
"""

from crewai import Agent, Task
from typing import Dict, Any, List

from app.agents.base import MedicalBillingAgent, MedicalBillingCrew
from app.tools import (
    StatementGenerationTool,
    PaymentProcessingTool,
    PatientLookupTool,
    PatientCommunicationTool,
    ClaimLookupTool,
    TeamCollaborationTool
)
from app.utils.logging import get_logger

logger = get_logger("agents.patient_billing")


def create_patient_billing_agent() -> Agent:
    """Create Patient Billing Agent using CrewAI framework"""
    
    # Initialize tools for patient billing
    tools = [
        StatementGenerationTool(),
        PaymentProcessingTool(),
        PatientLookupTool(),
        PatientCommunicationTool(),
        ClaimLookupTool(),
        TeamCollaborationTool()
    ]
    
    agent = MedicalBillingAgent(
        role="Patient Billing Specialist",
        goal=(
            "Generate accurate patient statements, process payments efficiently, "
            "manage payment plans and collections, and provide excellent customer "
            "service while maintaining compliance with billing regulations and "
            "patient privacy requirements."
        ),
        backstory=(
            "You are an expert in patient billing with deep knowledge of healthcare "
            "payment processing, collections regulations, and patient communication. "
            "You have extensive experience in statement generation, payment plan "
            "management, and dispute resolution. Your expertise includes automated "
            "billing workflows, multi-channel payment processing, and compassionate "
            "collections practices. You work closely with patients to resolve billing "
            "issues and ensure a positive financial experience while maximizing "
            "collections and maintaining compliance."
        ),
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=3,
        allow_delegation=True
    )
    
    return agent


class PatientBillingTasks:
    """Pre-defined tasks for Patient Billing Agent"""
    
    @staticmethod
    def generate_patient_statements(billing_data: Dict[str, Any]) -> Task:
        """Task to generate and distribute patient billing statements"""
        
        billing_json = str(billing_data)
        
        return Task(
            description=f"""
            Generate and distribute patient billing statements for the following accounts:
            
            {billing_json}
            
            Statement generation requirements:
            1. Create clear, itemized statements with service details
            2. Calculate patient responsibility after insurance payments
            3. Include payment options and instructions
            4. Apply appropriate aging categories and balances
            5. Generate personalized messages based on account status
            6. Ensure compliance with billing regulations and privacy rules
            7. Distribute via preferred communication channels (mail, email, portal)
            
            Use StatementGenerationTool to create professional statements.
            Use PatientLookupTool to verify current patient information.
            Use PatientCommunicationTool for statement delivery.
            """,
            expected_output=(
                "Statement generation report with created statements, delivery confirmations, "
                "patient contact summaries, and follow-up scheduling formatted as "
                "structured JSON with tracking information."
            ),
            agent=None
        )
    
    @staticmethod
    def process_patient_payments(payment_data: Dict[str, Any]) -> Task:
        """Task to process patient payments through various methods"""
        
        payment_json = str(payment_data)
        
        return Task(
            description=f"""
            Process patient payments through various payment methods:
            
            {payment_json}
            
            Payment processing requirements:
            1. Accept payments via credit card, ACH, check, and cash
            2. Apply payments to correct patient accounts and services
            3. Generate payment confirmations and receipts
            4. Handle payment plan installations and scheduling
            5. Process refunds and adjustments when appropriate
            6. Maintain PCI compliance and data security
            7. Update account balances and payment histories
            
            Use PaymentProcessingTool for secure payment processing.
            Use PatientCommunicationTool to send payment confirmations.
            """,
            expected_output=(
                "Payment processing report with transaction details, confirmation numbers, "
                "account updates, error handling, and receipt information formatted as "
                "structured JSON with audit trail."
            ),
            agent=None
        )
    
    @staticmethod
    def manage_payment_plans(plan_data: Dict[str, Any]) -> Task:
        """Task to set up and manage patient payment plans"""
        
        plan_json = str(plan_data)
        
        return Task(
            description=f"""
            Set up and manage patient payment plans for the following accounts:
            
            {plan_json}
            
            Payment plan management requirements:
            1. Evaluate patient financial situations and payment capacity
            2. Create customized payment plans with reasonable terms
            3. Set up automated payment schedules and reminders
            4. Monitor payment plan compliance and missed payments
            5. Provide options for plan modifications when needed
            6. Generate payment plan agreements and documentation
            7. Coordinate with collections team for defaulted plans
            
            Use StatementGenerationTool to create payment plan documents.
            Use PatientCommunicationTool for plan notifications and reminders.
            Use TeamCollaborationTool for collections coordination.
            """,
            expected_output=(
                "Payment plan management report with established plans, payment schedules, "
                "compliance tracking, modification requests, and escalation items "
                "formatted as structured JSON with monitoring alerts."
            ),
            agent=None
        )
    
    @staticmethod
    def handle_billing_inquiries(inquiry_data: Dict[str, Any]) -> Task:
        """Task to handle patient billing inquiries and disputes"""
        
        inquiry_json = str(inquiry_data)
        
        return Task(
            description=f"""
            Handle patient billing inquiries and resolve disputes for the following cases:
            
            {inquiry_json}
            
            Inquiry handling requirements:
            1. Research patient accounts and billing history
            2. Explain charges, insurance processing, and patient responsibility
            3. Resolve billing discrepancies and coding errors
            4. Process billing adjustments and corrections when appropriate
            5. Coordinate with insurance companies for coverage questions
            6. Document all interactions and resolutions
            7. Escalate complex issues to appropriate supervisors
            
            Use PatientLookupTool and ClaimLookupTool for account research.
            Use PatientCommunicationTool for customer interaction.
            Use TeamCollaborationTool for issue escalation.
            """,
            expected_output=(
                "Billing inquiry resolution report with case details, research findings, "
                "actions taken, customer satisfaction, and follow-up requirements "
                "formatted as structured JSON with resolution tracking."
            ),
            agent=None
        )
    
    @staticmethod
    def manage_collections_activities(collections_data: Dict[str, Any]) -> Task:
        """Task to manage collections activities and workflows"""
        
        collections_json = str(collections_data)
        
        return Task(
            description=f"""
            Manage collections activities for past-due accounts:
            
            {collections_json}
            
            Collections management requirements:
            1. Identify accounts requiring collections action
            2. Implement graduated collections approaches based on aging
            3. Send automated collection notices and reminders
            4. Conduct respectful collections calls following regulations
            5. Negotiate payment arrangements and settlements
            6. Coordinate with external collection agencies when appropriate
            7. Maintain compliance with FDCPA and state regulations
            
            Use PatientCommunicationTool for collections communications.
            Use PaymentProcessingTool for settlement processing.
            Use TeamCollaborationTool for agency coordination.
            """,
            expected_output=(
                "Collections management report with account statuses, contact results, "
                "payment arrangements, escalation decisions, and compliance documentation "
                "formatted as structured JSON with performance metrics."
            ),
            agent=None
        )


def create_patient_billing_crew(billing_data: Dict[str, Any]) -> MedicalBillingCrew:
    """Create a crew for comprehensive patient billing workflow"""
    
    # Create the billing agent
    billing_agent = create_patient_billing_agent()
    
    # Create tasks for the billing workflow
    tasks = [
        PatientBillingTasks.generate_patient_statements(billing_data),
        PatientBillingTasks.process_patient_payments(billing_data.get("payments", {})),
        PatientBillingTasks.manage_payment_plans(billing_data.get("payment_plans", {})),
        PatientBillingTasks.handle_billing_inquiries(billing_data.get("inquiries", {}))
    ]
    
    # Assign agent to tasks
    for task in tasks:
        task.agent = billing_agent
    
    # Create crew
    crew = MedicalBillingCrew(
        agents=[billing_agent],
        tasks=tasks,
        verbose=True,
        memory=True,
        process="sequential"
    )
    
    return crew


# Example usage function for testing
async def process_patient_billing(billing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process patient billing workflow"""
    
    try:
        # Create billing crew
        crew = create_patient_billing_crew(billing_data)
        
        # Execute billing workflow
        result = crew.kickoff()
        
        logger.info(f"Patient billing completed for period {billing_data.get('period', 'unknown')}")
        
        return {
            "status": "success",
            "period": billing_data.get("period"),
            "billing_result": result,
            "processed_at": billing_data.get("processed_at")
        }
        
    except Exception as e:
        error_msg = f"Patient billing failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "period": billing_data.get("period"),
            "error": error_msg
        } 