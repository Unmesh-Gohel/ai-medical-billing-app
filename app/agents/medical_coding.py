"""
Medical Coding Agent - CrewAI Implementation

This agent specializes in medical coding using ICD-10, CPT, and HCPCS codes
with NLP analysis and RAG-based code validation.
"""

from crewai import Agent, Task
from typing import Dict, Any, List

from app.agents.base import MedicalBillingAgent, MedicalBillingCrew
from app.tools import (
    MedicalCodingTool,
    DiagnosisLookupTool,
    ProcedureLookupTool,
    PatientLookupTool,
    TeamCollaborationTool
)
from app.utils.logging import get_logger

logger = get_logger("agents.medical_coding")


def create_medical_coding_agent() -> Agent:
    """Create Medical Coding Agent using CrewAI framework"""
    
    # Initialize tools for medical coding
    tools = [
        MedicalCodingTool(),
        DiagnosisLookupTool(),
        ProcedureLookupTool(),
        PatientLookupTool(),
        TeamCollaborationTool()
    ]
    
    agent = MedicalBillingAgent(
        role="Medical Coding Specialist",
        goal=(
            "Analyze clinical documentation and assign accurate ICD-10, CPT, and HCPCS codes "
            "to ensure optimal reimbursement while maintaining compliance with coding guidelines "
            "and regulatory requirements."
        ),
        backstory=(
            "You are an expert medical coder with extensive knowledge of ICD-10-CM, ICD-10-PCS, "
            "CPT, and HCPCS coding systems. You have deep understanding of medical terminology, "
            "anatomy, and disease processes. Your expertise includes DRG optimization, modifier "
            "application, and compliance with CMS guidelines. You use natural language processing "
            "and retrieval-augmented generation to ensure coding accuracy and consistency. "
            "You work collaboratively with providers to clarify documentation and optimize coding "
            "for both clinical accuracy and reimbursement."
        ),
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=3,
        allow_delegation=True
    )
    
    return agent


class MedicalCodingTasks:
    """Pre-defined tasks for Medical Coding Agent"""
    
    @staticmethod
    def analyze_clinical_documentation(encounter_data: Dict[str, Any]) -> Task:
        """Task to analyze clinical documentation and extract codeable elements"""
        
        encounter_json = str(encounter_data)
        
        return Task(
            description=f"""
            Analyze the following clinical documentation and extract all codeable elements:
            
            {encounter_json}
            
            Your analysis should include:
            1. Primary and secondary diagnoses identification
            2. Procedures and services performed  
            3. Medical decision making complexity
            4. Documentation quality assessment
            5. Missing documentation identification
            6. Coding opportunities and optimization suggestions
            
            Use the MedicalCodingTool to perform NLP analysis and extract relevant medical entities.
            Cross-reference findings with DiagnosisLookupTool and ProcedureLookupTool for validation.
            """,
            expected_output=(
                "Comprehensive analysis report including identified diagnoses, procedures, "
                "documentation quality score, missing elements, and optimization recommendations "
                "formatted as structured JSON."
            ),
            agent=None  # Will be assigned when task is created
        )
    
    @staticmethod
    def assign_diagnosis_codes(clinical_findings: Dict[str, Any]) -> Task:
        """Task to assign ICD-10-CM diagnosis codes"""
        
        findings_json = str(clinical_findings)
        
        return Task(
            description=f"""
            Assign accurate ICD-10-CM diagnosis codes for the following clinical findings:
            
            {findings_json}
            
            Requirements:
            1. Assign primary diagnosis code (most significant condition)
            2. Assign secondary diagnosis codes (comorbidities and complications)
            3. Ensure proper sequencing according to ICD-10 guidelines
            4. Apply appropriate 7th characters for injuries and external causes
            5. Validate codes for specificity and clinical validity
            6. Check for code combinations and excludes notes
            7. Optimize DRG assignment when applicable
            
            Use DiagnosisLookupTool for code validation and guidelines.
            """,
            expected_output=(
                "Complete diagnosis coding assignment with ICD-10-CM codes, descriptions, "
                "sequencing rationale, DRG impact analysis, and documentation improvement "
                "suggestions formatted as structured JSON."
            ),
            agent=None
        )
    
    @staticmethod
    def assign_procedure_codes(procedure_data: Dict[str, Any]) -> Task:
        """Task to assign CPT and HCPCS procedure codes"""
        
        procedure_json = str(procedure_data)
        
        return Task(
            description=f"""
            Assign accurate CPT and HCPCS procedure codes for the following services:
            
            {procedure_json}
            
            Requirements:
            1. Identify all billable procedures and services
            2. Assign appropriate CPT codes with correct modifiers
            3. Apply HCPCS codes for supplies and equipment when applicable
            4. Ensure proper bundling and unbundling rules
            5. Validate medical necessity and coverage requirements
            6. Apply appropriate quantity and unit modifiers
            7. Check for global period and multiple procedure rules
            
            Use ProcedureLookupTool for code validation and modifier guidance.
            """,
            expected_output=(
                "Complete procedure coding assignment with CPT/HCPCS codes, modifiers, "
                "units, medical necessity validation, and reimbursement optimization "
                "recommendations formatted as structured JSON."
            ),
            agent=None
        )
    
    @staticmethod
    def validate_code_combinations(coding_data: Dict[str, Any]) -> Task:
        """Task to validate code combinations and compliance"""
        
        coding_json = str(coding_data)
        
        return Task(
            description=f"""
            Validate the following code combinations for compliance and optimization:
            
            {coding_json}
            
            Validation requirements:
            1. Check ICD-10 to CPT code compatibility
            2. Verify modifier usage and appropriateness
            3. Validate medical necessity relationships
            4. Check for NCCI edits and bundling issues
            5. Ensure LCD/NCD compliance
            6. Verify age/gender/anatomical appropriateness
            7. Optimize for maximum legitimate reimbursement
            
            Use both DiagnosisLookupTool and ProcedureLookupTool for cross-validation.
            """,
            expected_output=(
                "Comprehensive validation report with compliance status, identified issues, "
                "optimization opportunities, and final coding recommendations formatted "
                "as structured JSON."
            ),
            agent=None
        )
    
    @staticmethod
    def query_provider_documentation(query_data: Dict[str, Any]) -> Task:
        """Task to generate queries for missing or unclear documentation"""
        
        query_json = str(query_data)
        
        return Task(
            description=f"""
            Generate appropriate documentation queries for the provider based on coding analysis:
            
            {query_json}
            
            Query requirements:
            1. Identify specific documentation gaps
            2. Generate clear, actionable queries
            3. Prioritize queries by reimbursement impact
            4. Include coding rationale and guidelines
            5. Suggest specific documentation improvements
            6. Maintain professional and educational tone
            7. Reference applicable coding guidelines
            
            Use TeamCollaborationTool to coordinate with clinical staff.
            """,
            expected_output=(
                "Professional documentation query list with specific questions, coding "
                "rationale, potential impact, and suggested documentation improvements "
                "formatted as structured communication ready for provider review."
            ),
            agent=None
        )


def create_medical_coding_crew(encounter_data: Dict[str, Any]) -> MedicalBillingCrew:
    """Create a crew for comprehensive medical coding workflow"""
    
    # Create the coding agent
    coding_agent = create_medical_coding_agent()
    
    # Create tasks for the coding workflow
    tasks = [
        MedicalCodingTasks.analyze_clinical_documentation(encounter_data),
        MedicalCodingTasks.assign_diagnosis_codes(encounter_data.get("clinical_findings", {})),
        MedicalCodingTasks.assign_procedure_codes(encounter_data.get("procedures", {})),
        MedicalCodingTasks.validate_code_combinations(encounter_data.get("proposed_codes", {}))
    ]
    
    # Assign agent to tasks
    for task in tasks:
        task.agent = coding_agent
    
    # Create crew
    crew = MedicalBillingCrew(
        agents=[coding_agent],
        tasks=tasks,
        verbose=True,
        memory=True,
        process="sequential"
    )
    
    return crew


# Example usage function for testing
async def process_medical_coding(encounter_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process medical coding for an encounter"""
    
    try:
        # Create coding crew
        crew = create_medical_coding_crew(encounter_data)
        
        # Execute coding workflow
        result = crew.kickoff()
        
        logger.info(f"Medical coding completed for encounter {encounter_data.get('encounter_id', 'unknown')}")
        
        return {
            "status": "success",
            "encounter_id": encounter_data.get("encounter_id"),
            "coding_result": result,
            "processed_at": encounter_data.get("processed_at")
        }
        
    except Exception as e:
        error_msg = f"Medical coding failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error", 
            "encounter_id": encounter_data.get("encounter_id"),
            "error": error_msg
        } 