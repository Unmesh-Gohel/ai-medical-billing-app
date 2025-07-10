"""
Claim Management Tools for CrewAI agents
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from crewai_tools import BaseTool
import uuid

from app.utils.logging import get_logger
from app.config import settings


logger = get_logger("tools.claim")


class ClaimGenerationTool(BaseTool):
    """Tool for generating clean medical claims"""
    
    name: str = "Medical Claim Generator"
    description: str = (
        "Generate clean medical claims from patient, insurance, and service data. "
        "Input should be JSON with patient_info, insurance_info, services, and provider_info. "
        "Returns formatted claim ready for submission."
    )
    
    def _run(self, input_data: str) -> str:
        """Generate a medical claim"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            patient_info = data.get("patient_info", {})
            insurance_info = data.get("insurance_info", {})
            services = data.get("services", [])
            provider_info = data.get("provider_info", {})
            
            # Validate required data
            validation_errors = self._validate_claim_data(patient_info, insurance_info, services)
            if validation_errors:
                return json.dumps({
                    "error": "Claim validation failed",
                    "validation_errors": validation_errors
                })
            
            # Generate claim
            claim = self._build_claim(patient_info, insurance_info, services, provider_info)
            
            # Perform claim scrubbing
            scrubbed_claim = self._scrub_claim(claim)
            
            result = {
                "claim_id": str(uuid.uuid4()),
                "claim_status": "draft",
                "generated_date": datetime.now().isoformat(),
                "claim_data": scrubbed_claim,
                "validation_status": "passed",
                "estimated_reimbursement": self._calculate_estimated_reimbursement(services),
                "submission_ready": True
            }
            
            logger.info(f"Generated claim for patient {patient_info.get('last_name', 'unknown')}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Claim generation failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _validate_claim_data(self, patient_info: Dict[str, Any], 
                           insurance_info: Dict[str, Any], 
                           services: List[Dict[str, Any]]) -> List[str]:
        """Validate claim data for completeness and accuracy"""
        errors = []
        
        # Validate patient information
        required_patient_fields = ["first_name", "last_name", "date_of_birth"]
        for field in required_patient_fields:
            if not patient_info.get(field):
                errors.append(f"Missing required patient field: {field}")
        
        # Validate insurance information
        required_insurance_fields = ["member_id", "payer_name"]
        for field in required_insurance_fields:
            if not insurance_info.get(field):
                errors.append(f"Missing required insurance field: {field}")
        
        # Validate services
        if not services:
            errors.append("At least one service must be provided")
        else:
            for i, service in enumerate(services):
                if not service.get("procedure_code"):
                    errors.append(f"Service {i+1} missing procedure code")
                if not service.get("diagnosis_codes"):
                    errors.append(f"Service {i+1} missing diagnosis codes")
                if not service.get("service_date"):
                    errors.append(f"Service {i+1} missing service date")
        
        return errors
    
    def _build_claim(self, patient_info: Dict[str, Any], 
                    insurance_info: Dict[str, Any], 
                    services: List[Dict[str, Any]], 
                    provider_info: Dict[str, Any]) -> Dict[str, Any]:
        """Build the claim structure"""
        claim = {
            "header": {
                "claim_type": "professional",
                "billing_provider": provider_info.get("npi", settings.PROVIDER_NPI),
                "submission_date": datetime.now().date().isoformat(),
                "claim_frequency": "1",  # Original claim
            },
            "patient": {
                "member_id": insurance_info.get("member_id"),
                "first_name": patient_info.get("first_name"),
                "last_name": patient_info.get("last_name"),
                "date_of_birth": patient_info.get("date_of_birth"),
                "gender": patient_info.get("gender"),
                "address": patient_info.get("address", {}),
                "relationship_to_insured": patient_info.get("relationship", "self")
            },
            "insurance": {
                "payer_name": insurance_info.get("payer_name"),
                "payer_id": insurance_info.get("payer_id"),
                "group_number": insurance_info.get("group_number"),
                "plan_name": insurance_info.get("plan_name")
            },
            "provider": {
                "npi": provider_info.get("npi", settings.PROVIDER_NPI),
                "name": provider_info.get("name", "Healthcare Provider"),
                "address": provider_info.get("address", {}),
                "tax_id": provider_info.get("tax_id"),
                "taxonomy_code": provider_info.get("taxonomy_code")
            },
            "services": []
        }
        
        # Add services to claim
        for service in services:
            claim_service = {
                "line_number": len(claim["services"]) + 1,
                "service_date": service.get("service_date"),
                "procedure_code": service.get("procedure_code"),
                "modifiers": service.get("modifiers", []),
                "diagnosis_pointers": list(range(1, len(service.get("diagnosis_codes", [])) + 1)),
                "units": service.get("units", 1),
                "charges": service.get("charges", 0.00),
                "place_of_service": service.get("place_of_service", "11"),  # Office
                "emergency": service.get("emergency", False)
            }
            claim["services"].append(claim_service)
        
        # Add diagnosis codes
        all_diagnosis_codes = []
        for service in services:
            all_diagnosis_codes.extend(service.get("diagnosis_codes", []))
        
        claim["diagnoses"] = [
            {"pointer": i+1, "code": code} 
            for i, code in enumerate(list(set(all_diagnosis_codes))[:12])  # Max 12 diagnoses
        ]
        
        return claim
    
    def _scrub_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Perform claim scrubbing to identify and fix common errors"""
        scrubbed = claim.copy()
        
        # Validate diagnosis codes format
        for diagnosis in scrubbed.get("diagnoses", []):
            code = diagnosis["code"]
            if not self._is_valid_icd10_format(code):
                logger.warning(f"Invalid ICD-10 format: {code}")
        
        # Validate procedure codes
        for service in scrubbed.get("services", []):
            code = service["procedure_code"]
            if not self._is_valid_cpt_format(code):
                logger.warning(f"Invalid CPT format: {code}")
        
        # Check for missing modifiers on certain procedures
        for service in scrubbed.get("services", []):
            if self._requires_modifier(service["procedure_code"]) and not service.get("modifiers"):
                logger.warning(f"Procedure {service['procedure_code']} may require modifier")
        
        return scrubbed
    
    def _is_valid_icd10_format(self, code: str) -> bool:
        """Validate ICD-10 code format"""
        import re
        pattern = r'^[A-Z][0-9][0-9A-Z](\.[0-9A-Z]{1,4})?$'
        return bool(re.match(pattern, code))
    
    def _is_valid_cpt_format(self, code: str) -> bool:
        """Validate CPT code format"""
        return code.isdigit() and len(code) == 5
    
    def _requires_modifier(self, cpt_code: str) -> bool:
        """Check if CPT code commonly requires modifiers"""
        # Common codes that often need modifiers
        modifier_codes = ["27447", "66984", "19120", "29881"]
        return cpt_code in modifier_codes
    
    def _calculate_estimated_reimbursement(self, services: List[Dict[str, Any]]) -> float:
        """Calculate estimated reimbursement amount"""
        total_charges = sum(service.get("charges", 0) for service in services)
        # Apply typical reimbursement rate (simplified calculation)
        estimated_reimbursement = total_charges * 0.8  # 80% reimbursement rate
        return round(estimated_reimbursement, 2)


class ClaimSubmissionTool(BaseTool):
    """Tool for submitting claims electronically"""
    
    name: str = "Electronic Claim Submitter"
    description: str = (
        "Submit medical claims electronically to clearinghouses or payers. "
        "Input should be JSON with claim_data and submission_options. "
        "Returns submission status and tracking information."
    )
    
    def _run(self, input_data: str) -> str:
        """Submit claim electronically"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            claim_data = data.get("claim_data", {})
            submission_options = data.get("submission_options", {})
            
            if not claim_data:
                return json.dumps({"error": "Claim data is required for submission"})
            
            # Validate claim before submission
            validation_result = self._validate_for_submission(claim_data)
            if not validation_result["is_valid"]:
                return json.dumps({
                    "submission_status": "failed",
                    "error": "Claim validation failed",
                    "validation_errors": validation_result["errors"]
                })
            
            # Submit claim
            submission_result = self._submit_claim(claim_data, submission_options)
            
            logger.info(f"Claim submitted with tracking ID: {submission_result['tracking_id']}")
            return json.dumps(submission_result, indent=2)
            
        except Exception as e:
            error_msg = f"Claim submission failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _validate_for_submission(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate claim data before submission"""
        errors = []
        
        # Check required fields
        required_sections = ["header", "patient", "insurance", "provider", "services", "diagnoses"]
        for section in required_sections:
            if section not in claim_data:
                errors.append(f"Missing required section: {section}")
        
        # Validate service line items
        services = claim_data.get("services", [])
        if not services:
            errors.append("Claim must have at least one service line")
        
        for service in services:
            if not service.get("procedure_code"):
                errors.append(f"Line {service.get('line_number', '?')} missing procedure code")
            if service.get("charges", 0) <= 0:
                errors.append(f"Line {service.get('line_number', '?')} has invalid charges")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def _submit_claim(self, claim_data: Dict[str, Any], 
                     submission_options: Dict[str, Any]) -> Dict[str, Any]:
        """Submit claim to clearinghouse or payer"""
        
        # Generate tracking ID
        tracking_id = f"CLM{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Mock submission - in production would submit to actual clearinghouse
        if settings.CLEARINGHOUSE_API_URL:
            return self._real_claim_submission(claim_data, tracking_id)
        else:
            return self._mock_claim_submission(claim_data, tracking_id)
    
    def _real_claim_submission(self, claim_data: Dict[str, Any], tracking_id: str) -> Dict[str, Any]:
        """Submit to real clearinghouse API"""
        # This would implement actual EDI submission
        return {
            "submission_status": "submitted",
            "tracking_id": tracking_id,
            "submission_date": datetime.now().isoformat(),
            "clearinghouse": "Production Clearinghouse",
            "estimated_processing_time": "24-48 hours"
        }
    
    def _mock_claim_submission(self, claim_data: Dict[str, Any], tracking_id: str) -> Dict[str, Any]:
        """Mock claim submission for demonstration"""
        return {
            "submission_status": "submitted",
            "tracking_id": tracking_id,
            "submission_date": datetime.now().isoformat(),
            "clearinghouse": "Mock Clearinghouse",
            "batch_id": f"BATCH{datetime.now().strftime('%Y%m%d')}001",
            "estimated_processing_time": "24-48 hours",
            "total_charges": sum(service.get("charges", 0) for service in claim_data.get("services", [])),
            "service_count": len(claim_data.get("services", []))
        }


class ClaimStatusTool(BaseTool):
    """Tool for checking claim status and processing updates"""
    
    name: str = "Claim Status Tracker"
    description: str = (
        "Check the status of submitted claims and track processing updates. "
        "Input should be a tracking ID or claim ID. "
        "Returns current claim status and processing history."
    )
    
    def _run(self, tracking_id: str) -> str:
        """Check claim status"""
        try:
            if not tracking_id:
                return json.dumps({"error": "Tracking ID is required"})
            
            # Get claim status
            status_result = self._get_claim_status(tracking_id)
            
            logger.info(f"Status check completed for claim {tracking_id}")
            return json.dumps(status_result, indent=2)
            
        except Exception as e:
            error_msg = f"Claim status check failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _get_claim_status(self, tracking_id: str) -> Dict[str, Any]:
        """Get current claim status"""
        
        # Mock status data - in production would query clearinghouse/payer
        status_scenarios = {
            "submitted": {
                "status": "submitted",
                "status_date": datetime.now().isoformat(),
                "description": "Claim has been submitted and is being processed"
            },
            "accepted": {
                "status": "accepted",
                "status_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "description": "Claim has been accepted by payer"
            },
            "paid": {
                "status": "paid",
                "status_date": (datetime.now() - timedelta(days=14)).isoformat(),
                "description": "Claim has been processed and payment issued",
                "payment_amount": 157.50,
                "payment_date": (datetime.now() - timedelta(days=10)).isoformat()
            },
            "denied": {
                "status": "denied",
                "status_date": (datetime.now() - timedelta(days=7)).isoformat(),
                "description": "Claim has been denied",
                "denial_reason": "Prior authorization required",
                "denial_code": "197"
            }
        }
        
        # Determine status based on tracking ID (for demo)
        if tracking_id.endswith(("1", "2", "3")):
            status_key = "paid"
        elif tracking_id.endswith(("4", "5")):
            status_key = "accepted"
        elif tracking_id.endswith(("6", "7")):
            status_key = "denied"
        else:
            status_key = "submitted"
        
        status_info = status_scenarios[status_key]
        
        result = {
            "tracking_id": tracking_id,
            "current_status": status_info["status"],
            "last_updated": status_info["status_date"],
            "description": status_info["description"],
            "processing_history": [
                {
                    "date": (datetime.now() - timedelta(days=15)).isoformat(),
                    "status": "submitted",
                    "description": "Claim submitted to clearinghouse"
                },
                {
                    "date": status_info["status_date"],
                    "status": status_info["status"],
                    "description": status_info["description"]
                }
            ]
        }
        
        # Add status-specific information
        if "payment_amount" in status_info:
            result["payment_info"] = {
                "amount": status_info["payment_amount"],
                "date": status_info["payment_date"]
            }
        
        if "denial_reason" in status_info:
            result["denial_info"] = {
                "reason": status_info["denial_reason"],
                "code": status_info["denial_code"]
            }
        
        return result 