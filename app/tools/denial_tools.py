"""
Denial Management and Appeal Tools for CrewAI agents
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from crewai_tools import BaseTool

from app.utils.logging import get_logger


logger = get_logger("tools.denial")


class DenialAnalysisTool(BaseTool):
    """Tool for analyzing claim denials and identifying resolution strategies"""
    
    name: str = "Denial Analysis Engine"
    description: str = (
        "Analyze claim denials to identify root causes and recommend resolution strategies. "
        "Input should be JSON with denial_info and claim_data. "
        "Returns detailed analysis and recommended actions."
    )
    
    def _run(self, input_data: str) -> str:
        """Analyze claim denial"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            denial_info = data.get("denial_info", {})
            claim_data = data.get("claim_data", {})
            
            if not denial_info:
                return json.dumps({"error": "Denial information is required"})
            
            # Analyze denial
            analysis = self._analyze_denial(denial_info, claim_data)
            
            logger.info(f"Denial analysis completed for reason: {denial_info.get('reason', 'unknown')}")
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            error_msg = f"Denial analysis failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _analyze_denial(self, denial_info: Dict[str, Any], claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze denial and determine resolution strategy"""
        
        denial_code = denial_info.get("code", "")
        denial_reason = denial_info.get("reason", "")
        
        # Get denial category and resolution strategy
        category = self._categorize_denial(denial_code, denial_reason)
        resolution_strategy = self._get_resolution_strategy(category, denial_code)
        
        # Analyze claim data for specific issues
        claim_issues = self._identify_claim_issues(claim_data, denial_info)
        
        # Determine appeal probability
        appeal_probability = self._calculate_appeal_probability(category, claim_issues)
        
        analysis = {
            "denial_code": denial_code,
            "denial_reason": denial_reason,
            "category": category,
            "severity": self._get_denial_severity(category),
            "resolution_strategy": resolution_strategy,
            "claim_issues": claim_issues,
            "appeal_probability": appeal_probability,
            "recommended_actions": self._get_recommended_actions(category, claim_issues),
            "required_documentation": self._get_required_documentation(category),
            "time_to_resolve": self._estimate_resolution_time(category),
            "analysis_date": datetime.now().isoformat()
        }
        
        return analysis
    
    def _categorize_denial(self, denial_code: str, denial_reason: str) -> str:
        """Categorize denial based on code and reason"""
        
        # Common denial categories
        if denial_code in ["1", "4", "18", "197"]:
            return "authorization_required"
        elif denial_code in ["11", "96", "109"]:
            return "medical_necessity"
        elif denial_code in ["16", "50", "119"]:
            return "coverage_limitation"
        elif denial_code in ["27", "29", "31"]:
            return "coding_error"
        elif denial_code in ["140", "142", "149"]:
            return "documentation_insufficient"
        elif denial_code in ["22", "23", "24"]:
            return "duplicate_claim"
        elif denial_code in ["26", "41", "125"]:
            return "patient_eligibility"
        else:
            # Analyze by reason text
            reason_lower = denial_reason.lower()
            if "authorization" in reason_lower or "approval" in reason_lower:
                return "authorization_required"
            elif "medical necessity" in reason_lower:
                return "medical_necessity"
            elif "coverage" in reason_lower or "benefit" in reason_lower:
                return "coverage_limitation"
            elif "code" in reason_lower or "coding" in reason_lower:
                return "coding_error"
            elif "documentation" in reason_lower or "records" in reason_lower:
                return "documentation_insufficient"
            else:
                return "other"
    
    def _get_resolution_strategy(self, category: str, denial_code: str) -> Dict[str, Any]:
        """Get resolution strategy based on denial category"""
        
        strategies = {
            "authorization_required": {
                "primary_action": "obtain_authorization",
                "steps": [
                    "Contact payer to obtain retroactive authorization",
                    "Submit authorization request with clinical documentation",
                    "Resubmit claim with authorization number"
                ],
                "success_rate": 75
            },
            "medical_necessity": {
                "primary_action": "provide_clinical_justification",
                "steps": [
                    "Gather additional clinical documentation",
                    "Obtain physician letter supporting medical necessity",
                    "Submit appeal with comprehensive clinical rationale"
                ],
                "success_rate": 60
            },
            "coverage_limitation": {
                "primary_action": "verify_benefits",
                "steps": [
                    "Review patient's benefit coverage",
                    "Check if alternative covered services available",
                    "Appeal with benefit interpretation argument if applicable"
                ],
                "success_rate": 45
            },
            "coding_error": {
                "primary_action": "correct_and_resubmit",
                "steps": [
                    "Review and correct medical codes",
                    "Ensure proper code linkage",
                    "Resubmit corrected claim"
                ],
                "success_rate": 85
            },
            "documentation_insufficient": {
                "primary_action": "submit_additional_records",
                "steps": [
                    "Identify required documentation",
                    "Obtain missing records from provider",
                    "Submit appeal with complete documentation"
                ],
                "success_rate": 70
            },
            "duplicate_claim": {
                "primary_action": "verify_claim_status",
                "steps": [
                    "Check if original claim was processed",
                    "If not processed, resubmit with corrected dates",
                    "If processed, verify payment was received"
                ],
                "success_rate": 90
            },
            "patient_eligibility": {
                "primary_action": "verify_eligibility",
                "steps": [
                    "Obtain updated eligibility verification",
                    "Correct patient information if needed",
                    "Resubmit with proper eligibility documentation"
                ],
                "success_rate": 80
            },
            "other": {
                "primary_action": "manual_review",
                "steps": [
                    "Review denial reason carefully",
                    "Research payer-specific requirements",
                    "Consult with billing specialist"
                ],
                "success_rate": 50
            }
        }
        
        return strategies.get(category, strategies["other"])
    
    def _identify_claim_issues(self, claim_data: Dict[str, Any], denial_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify specific issues in the claim that may have caused denial"""
        issues = []
        
        # Check for common claim issues
        services = claim_data.get("services", [])
        
        for service in services:
            # Check for missing modifiers
            if self._requires_modifier(service.get("procedure_code", "")):
                if not service.get("modifiers"):
                    issues.append({
                        "type": "missing_modifier",
                        "description": f"Procedure {service['procedure_code']} may require modifier",
                        "severity": "medium"
                    })
            
            # Check for unusual charges
            charges = service.get("charges", 0)
            if charges > 10000:  # Unusually high charges
                issues.append({
                    "type": "high_charges",
                    "description": f"Unusually high charges: ${charges}",
                    "severity": "medium"
                })
        
        # Check diagnosis code count
        diagnoses = claim_data.get("diagnoses", [])
        if len(diagnoses) == 0:
            issues.append({
                "type": "missing_diagnosis",
                "description": "No diagnosis codes provided",
                "severity": "high"
            })
        
        return issues
    
    def _calculate_appeal_probability(self, category: str, claim_issues: List[Dict[str, str]]) -> float:
        """Calculate probability of successful appeal"""
        
        base_probabilities = {
            "authorization_required": 0.75,
            "medical_necessity": 0.60,
            "coverage_limitation": 0.45,
            "coding_error": 0.85,
            "documentation_insufficient": 0.70,
            "duplicate_claim": 0.90,
            "patient_eligibility": 0.80,
            "other": 0.50
        }
        
        base_prob = base_probabilities.get(category, 0.50)
        
        # Adjust based on claim issues
        issue_penalty = len([i for i in claim_issues if i["severity"] == "high"]) * 0.1
        base_prob = max(0.1, base_prob - issue_penalty)
        
        return round(base_prob, 2)
    
    def _get_denial_severity(self, category: str) -> str:
        """Get denial severity level"""
        high_severity = ["medical_necessity", "coverage_limitation"]
        medium_severity = ["authorization_required", "documentation_insufficient"]
        
        if category in high_severity:
            return "high"
        elif category in medium_severity:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_actions(self, category: str, claim_issues: List[Dict[str, str]]) -> List[str]:
        """Get recommended immediate actions"""
        actions = []
        
        if category == "coding_error":
            actions.append("Review and correct medical codes immediately")
        elif category == "authorization_required":
            actions.append("Contact payer to request retroactive authorization")
        elif category == "documentation_insufficient":
            actions.append("Gather additional clinical documentation")
        
        # Add actions based on claim issues
        for issue in claim_issues:
            if issue["type"] == "missing_modifier":
                actions.append("Add appropriate modifier to procedure code")
            elif issue["type"] == "missing_diagnosis":
                actions.append("Add missing diagnosis codes")
        
        return actions
    
    def _get_required_documentation(self, category: str) -> List[str]:
        """Get required documentation for appeal"""
        documentation = {
            "authorization_required": [
                "Authorization request form",
                "Clinical notes supporting medical necessity"
            ],
            "medical_necessity": [
                "Physician documentation of medical necessity",
                "Clinical guidelines supporting treatment",
                "Patient medical history"
            ],
            "coverage_limitation": [
                "Benefit verification",
                "Alternative treatment documentation"
            ],
            "coding_error": [
                "Corrected claim form",
                "Coding justification"
            ],
            "documentation_insufficient": [
                "Complete medical records",
                "Operative reports if applicable",
                "Diagnostic test results"
            ],
            "duplicate_claim": [
                "Original claim tracking information",
                "Proof of non-payment"
            ],
            "patient_eligibility": [
                "Updated eligibility verification",
                "Corrected patient information"
            ]
        }
        
        return documentation.get(category, ["Appeal letter", "Supporting documentation"])
    
    def _estimate_resolution_time(self, category: str) -> str:
        """Estimate time to resolve denial"""
        timeframes = {
            "coding_error": "1-2 weeks",
            "duplicate_claim": "1-2 weeks", 
            "patient_eligibility": "2-3 weeks",
            "authorization_required": "3-4 weeks",
            "documentation_insufficient": "4-6 weeks",
            "medical_necessity": "6-8 weeks",
            "coverage_limitation": "8-12 weeks",
            "other": "4-8 weeks"
        }
        
        return timeframes.get(category, "4-8 weeks")
    
    def _requires_modifier(self, cpt_code: str) -> bool:
        """Check if CPT code commonly requires modifiers"""
        modifier_codes = ["27447", "66984", "19120", "29881"]
        return cpt_code in modifier_codes


class AppealGenerationTool(BaseTool):
    """Tool for generating formal appeals for denied claims"""
    
    name: str = "Appeal Letter Generator"
    description: str = (
        "Generate formal appeal letters for denied claims based on denial analysis. "
        "Input should be JSON with denial_analysis and claim_data. "
        "Returns formatted appeal letter and submission instructions."
    )
    
    def _run(self, input_data: str) -> str:
        """Generate appeal letter"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            denial_analysis = data.get("denial_analysis", {})
            claim_data = data.get("claim_data", {})
            
            if not denial_analysis:
                return json.dumps({"error": "Denial analysis is required for appeal generation"})
            
            # Generate appeal
            appeal = self._generate_appeal(denial_analysis, claim_data)
            
            logger.info("Appeal letter generated successfully")
            return json.dumps(appeal, indent=2)
            
        except Exception as e:
            error_msg = f"Appeal generation failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _generate_appeal(self, denial_analysis: Dict[str, Any], claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate formal appeal letter"""
        
        category = denial_analysis.get("category", "")
        appeal_letter = self._create_appeal_letter(denial_analysis, claim_data)
        
        appeal = {
            "appeal_id": f"APP{datetime.now().strftime('%Y%m%d')}{datetime.now().microsecond}",
            "generated_date": datetime.now().isoformat(),
            "appeal_letter": appeal_letter,
            "submission_deadline": (datetime.now() + timedelta(days=30)).date().isoformat(),
            "required_attachments": denial_analysis.get("required_documentation", []),
            "submission_method": "mail",  # Could be electronic for some payers
            "estimated_response_time": denial_analysis.get("time_to_resolve", "4-8 weeks"),
            "appeal_probability": denial_analysis.get("appeal_probability", 0.5)
        }
        
        return appeal
    
    def _create_appeal_letter(self, denial_analysis: Dict[str, Any], claim_data: Dict[str, Any]) -> str:
        """Create the actual appeal letter text"""
        
        patient_info = claim_data.get("patient", {})
        insurance_info = claim_data.get("insurance", {})
        
        letter = f"""
[Date: {datetime.now().strftime('%B %d, %Y')}]

[Insurance Company Name]
Appeals Department
[Address]

RE: Appeal for Denied Claim
Patient: {patient_info.get('first_name', '')} {patient_info.get('last_name', '')}
Member ID: {patient_info.get('member_id', '')}
Claim Number: [Claim Number]
Date of Service: [Service Date]

Dear Appeals Review Committee,

I am writing to formally appeal the denial of the above-referenced claim. The claim was denied with reason code {denial_analysis.get('denial_code', '')}: "{denial_analysis.get('denial_reason', '')}".

{self._get_appeal_body(denial_analysis, claim_data)}

Based on the above information, I respectfully request that you reverse the denial decision and process this claim for payment. The services provided were medically necessary, properly documented, and covered under the patient's benefit plan.

If you require any additional information or documentation, please contact our office immediately. We look forward to your prompt response and favorable reconsideration of this claim.

Sincerely,

[Provider Name]
[Title]
[Contact Information]

Enclosures: [List of attached documents]
        """
        
        return letter.strip()
    
    def _get_appeal_body(self, denial_analysis: Dict[str, Any], claim_data: Dict[str, Any]) -> str:
        """Generate appeal body based on denial category"""
        
        category = denial_analysis.get("category", "")
        
        if category == "medical_necessity":
            return """
The services provided were medically necessary based on the patient's clinical presentation and condition. The treatment rendered follows established clinical guidelines and represents the appropriate standard of care for this patient's specific medical needs.

Clinical documentation supporting medical necessity has been included with this appeal. The patient's condition required the specific intervention provided, and alternative treatments would not have been appropriate or effective in this case.
            """
        
        elif category == "authorization_required":
            return """
While we acknowledge that prior authorization may have been required for this service, the urgent nature of the patient's condition necessitated immediate treatment. We are requesting retroactive authorization based on the medical emergency circumstances.

The patient's clinical condition required immediate intervention, and delaying treatment to obtain prior authorization would have compromised patient safety and outcomes.
            """
        
        elif category == "coding_error":
            return """
Upon review of the denial, we have identified and corrected the coding error in the original claim submission. The correct codes have been verified and properly linked to support the services provided.

The corrected claim accurately reflects the services rendered and should be processed according to the patient's benefit coverage.
            """
        
        elif category == "documentation_insufficient":
            return """
Additional clinical documentation has been obtained and is included with this appeal to provide complete information regarding the services rendered. The medical records clearly document the medical necessity and appropriateness of the treatment provided.

The comprehensive documentation demonstrates that all services were properly performed and medically indicated based on the patient's condition.
            """
        
        else:
            return """
The denial of this claim appears to be in error based on our review of the patient's benefits and the services provided. The treatment rendered was covered under the patient's plan and was medically appropriate for the diagnosed condition.

We respectfully request reconsideration of this denial and processing of the claim for payment as originally submitted.
            """ 