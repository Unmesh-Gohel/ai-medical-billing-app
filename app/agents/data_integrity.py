"""
Data Integrity Agent - CrewAI Implementation

This agent specializes in patient records management, data quality assurance,
and EHR synchronization with automated validation and error correction.
"""

from crewai import Agent, Task
from typing import Dict, Any, List

from app.agents.base import MedicalBillingAgent, MedicalBillingCrew
from app.tools import (
    PatientLookupTool,
    ClaimLookupTool,
    EligibilityCheckTool,
    OCRTool,
    TeamCollaborationTool
)
from app.utils.logging import get_logger

logger = get_logger("agents.data_integrity")


def create_data_integrity_agent() -> Agent:
    """Create Data Integrity Agent using CrewAI framework"""
    
    # Initialize tools for data integrity
    tools = [
        PatientLookupTool(),
        ClaimLookupTool(),
        EligibilityCheckTool(),
        OCRTool(),
        TeamCollaborationTool()
    ]
    
    agent = MedicalBillingAgent(
        role="Data Integrity Specialist",
        goal=(
            "Ensure data accuracy and consistency across all systems, maintain patient "
            "record integrity, synchronize EHR data, and implement automated quality "
            "assurance processes to support reliable billing and clinical operations."
        ),
        backstory=(
            "You are an expert in healthcare data management with deep knowledge of data "
            "quality standards, EHR systems, and interoperability protocols. You have "
            "extensive experience in data validation, cleansing, and synchronization "
            "across multiple healthcare systems. Your expertise includes automated "
            "error detection, duplicate record resolution, and HIPAA-compliant data "
            "handling. You work closely with IT teams and clinical staff to ensure "
            "data accuracy and support seamless information flow between systems."
        ),
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=3,
        allow_delegation=True
    )
    
    return agent


class DataIntegrityTasks:
    """Pre-defined tasks for Data Integrity Agent"""
    
    @staticmethod
    def validate_patient_records(validation_data: Dict[str, Any]) -> Task:
        """Task to validate patient records for accuracy and completeness"""
        
        validation_json = str(validation_data)
        
        return Task(
            description=f"""
            Validate patient records for accuracy and completeness from the following data:
            
            {validation_json}
            
            Validation requirements:
            1. Verify demographic information accuracy and consistency
            2. Check insurance information and eligibility status
            3. Validate contact information and communication preferences
            4. Ensure proper record linking and duplicate detection
            5. Verify medical record number assignments and uniqueness
            6. Check data format compliance and standardization
            7. Identify missing or incomplete required fields
            
            Use PatientLookupTool to verify existing records.
            Use EligibilityCheckTool to validate insurance information.
            """,
            expected_output=(
                "Patient record validation report with accuracy scores, identified errors, "
                "missing data, duplicate records, and correction recommendations formatted "
                "as structured JSON with validation metrics."
            ),
            agent=None
        )
    
    @staticmethod
    def synchronize_ehr_data(sync_data: Dict[str, Any]) -> Task:
        """Task to synchronize data between EHR and billing systems"""
        
        sync_json = str(sync_data)
        
        return Task(
            description=f"""
            Synchronize data between EHR and billing systems for the following records:
            
            {sync_json}
            
            Synchronization requirements:
            1. Compare data consistency between EHR and billing systems
            2. Identify discrepancies and data conflicts
            3. Implement automated data reconciliation rules
            4. Update records with authoritative data sources
            5. Maintain audit trails for all data changes
            6. Ensure real-time synchronization for critical fields
            7. Generate synchronization status reports
            
            Use PatientLookupTool to access current records.
            Use TeamCollaborationTool to coordinate system updates.
            """,
            expected_output=(
                "EHR synchronization report with reconciled records, identified conflicts, "
                "automated corrections, manual review items, and system status updates "
                "formatted as structured JSON with synchronization metrics."
            ),
            agent=None
        )
    
    @staticmethod
    def perform_data_quality_audit(audit_data: Dict[str, Any]) -> Task:
        """Task to perform comprehensive data quality audits"""
        
        audit_json = str(audit_data)
        
        return Task(
            description=f"""
            Perform comprehensive data quality audit on the following datasets:
            
            {audit_json}
            
            Data quality audit requirements:
            1. Assess data completeness across all required fields
            2. Evaluate data accuracy against source documents
            3. Check data consistency and standardization compliance
            4. Identify data anomalies and outliers
            5. Measure data freshness and update frequencies
            6. Analyze data relationships and referential integrity
            7. Generate quality scorecards and trend analysis
            
            Use PatientLookupTool and ClaimLookupTool for data analysis.
            Use OCRTool to verify against source documents when available.
            """,
            expected_output=(
                "Data quality audit report with quality scores, completeness metrics, "
                "accuracy assessments, anomaly detection, and improvement recommendations "
                "formatted as structured JSON with quality indicators."
            ),
            agent=None
        )
    
    @staticmethod
    def resolve_duplicate_records(duplicate_data: Dict[str, Any]) -> Task:
        """Task to identify and resolve duplicate patient records"""
        
        duplicate_json = str(duplicate_data)
        
        return Task(
            description=f"""
            Identify and resolve duplicate patient records from the following data:
            
            {duplicate_json}
            
            Duplicate resolution requirements:
            1. Use advanced matching algorithms to identify potential duplicates
            2. Score duplicate probability based on multiple data points
            3. Analyze record creation patterns and data conflicts
            4. Determine authoritative records for merging decisions
            5. Implement safe merging procedures with backup protocols
            6. Update all related claims and billing records
            7. Generate resolution reports and audit documentation
            
            Use PatientLookupTool for comprehensive record analysis.
            Use TeamCollaborationTool for manual review coordination.
            """,
            expected_output=(
                "Duplicate resolution report with identified duplicates, confidence scores, "
                "merging decisions, affected records, and post-merge validation results "
                "formatted as structured JSON with resolution tracking."
            ),
            agent=None
        )
    
    @staticmethod
    def implement_data_governance(governance_data: Dict[str, Any]) -> Task:
        """Task to implement data governance policies and procedures"""
        
        governance_json = str(governance_data)
        
        return Task(
            description=f"""
            Implement data governance policies and procedures for the following areas:
            
            {governance_json}
            
            Data governance requirements:
            1. Establish data quality standards and validation rules
            2. Implement automated monitoring and alerting systems
            3. Create data stewardship roles and responsibilities
            4. Design data lifecycle management procedures
            5. Ensure HIPAA compliance and privacy protection
            6. Establish change management and version control
            7. Generate governance dashboards and compliance reports
            
            Use TeamCollaborationTool to coordinate with IT and compliance teams.
            """,
            expected_output=(
                "Data governance implementation plan with policies, procedures, monitoring "
                "systems, compliance measures, and performance metrics formatted as "
                "structured JSON with governance framework."
            ),
            agent=None
        )


def create_data_integrity_crew(integrity_data: Dict[str, Any]) -> MedicalBillingCrew:
    """Create a crew for comprehensive data integrity workflow"""
    
    # Create the integrity agent
    integrity_agent = create_data_integrity_agent()
    
    # Create tasks for the integrity workflow
    tasks = [
        DataIntegrityTasks.validate_patient_records(integrity_data),
        DataIntegrityTasks.synchronize_ehr_data(integrity_data.get("sync_data", {})),
        DataIntegrityTasks.perform_data_quality_audit(integrity_data.get("audit_data", {})),
        DataIntegrityTasks.resolve_duplicate_records(integrity_data.get("duplicate_data", {}))
    ]
    
    # Assign agent to tasks
    for task in tasks:
        task.agent = integrity_agent
    
    # Create crew
    crew = MedicalBillingCrew(
        agents=[integrity_agent],
        tasks=tasks,
        verbose=True,
        memory=True,
        process="sequential"
    )
    
    return crew


# Example usage function for testing
async def process_data_integrity(integrity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data integrity workflow"""
    
    try:
        # Create integrity crew
        crew = create_data_integrity_crew(integrity_data)
        
        # Execute integrity workflow
        result = crew.kickoff()
        
        logger.info(f"Data integrity processing completed for dataset {integrity_data.get('dataset_id', 'unknown')}")
        
        return {
            "status": "success",
            "dataset_id": integrity_data.get("dataset_id"),
            "integrity_result": result,
            "processed_at": integrity_data.get("processed_at")
        }
        
    except Exception as e:
        error_msg = f"Data integrity processing failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "dataset_id": integrity_data.get("dataset_id"),
            "error": error_msg
        } 