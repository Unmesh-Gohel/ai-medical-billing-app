"""
Eligibility and Insurance Verification Tools for CrewAI agents
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime, date
from crewai_tools import BaseTool
import asyncio
import aiohttp

from app.utils.logging import get_logger
from app.config import settings


logger = get_logger("tools.eligibility")


class EligibilityCheckTool(BaseTool):
    """Tool for checking patient eligibility with insurance payers"""
    
    name: str = "Insurance Eligibility Checker"
    description: str = (
        "Verify patient insurance eligibility and coverage. "
        "Input should be JSON with patient_info and insurance_info. "
        "Returns eligibility status, coverage details, and benefit information."
    )
    
    def _run(self, input_data: str) -> str:
        """Check patient eligibility with insurance payer"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            patient_info = data.get("patient_info", {})
            insurance_info = data.get("insurance_info", {})
            service_date = data.get("service_date", datetime.now().date().isoformat())
            
            # Validate required fields
            if not patient_info or not insurance_info:
                return json.dumps({
                    "error": "Both patient_info and insurance_info are required",
                    "eligibility_status": "failed"
                })
            
            # Perform eligibility check
            eligibility_result = asyncio.run(
                self._check_eligibility_async(patient_info, insurance_info, service_date)
            )
            
            logger.info(f"Eligibility check completed for patient {patient_info.get('member_id', 'unknown')}")
            return json.dumps(eligibility_result, indent=2)
            
        except Exception as e:
            error_msg = f"Eligibility check failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({
                "error": error_msg,
                "eligibility_status": "failed"
            })
    
    async def _check_eligibility_async(self, patient_info: Dict[str, Any], 
                                     insurance_info: Dict[str, Any], 
                                     service_date: str) -> Dict[str, Any]:
        """Perform async eligibility check"""
        
        # Build eligibility request
        request_data = {
            "transaction_code": "270",  # EDI transaction code for eligibility inquiry
            "patient": {
                "member_id": insurance_info.get("member_id", ""),
                "first_name": patient_info.get("first_name", ""),
                "last_name": patient_info.get("last_name", ""),
                "date_of_birth": patient_info.get("date_of_birth", ""),
                "gender": patient_info.get("gender", "")
            },
            "insurance": {
                "payer_id": insurance_info.get("payer_id", ""),
                "payer_name": insurance_info.get("payer_name", ""),
                "group_number": insurance_info.get("group_number", ""),
                "plan_name": insurance_info.get("plan_name", "")
            },
            "service_date": service_date,
            "provider_npi": settings.PROVIDER_NPI if hasattr(settings, 'PROVIDER_NPI') else ""
        }
        
        # For demo purposes, simulate eligibility check
        # In production, this would make API calls to clearinghouse or payer
        if settings.CLEARINGHOUSE_API_URL:
            return await self._real_eligibility_check(request_data)
        else:
            return self._mock_eligibility_check(request_data)
    
    async def _real_eligibility_check(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make real API call to clearinghouse for eligibility"""
        
        headers = {
            "Authorization": f"Bearer {settings.CLEARINGHOUSE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{settings.CLEARINGHOUSE_API_URL}/eligibility",
                    json=request_data,
                    headers=headers,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_eligibility_response(result)
                    else:
                        error_text = await response.text()
                        return {
                            "eligibility_status": "failed",
                            "error": f"API error {response.status}: {error_text}",
                            "is_eligible": False
                        }
                        
        except asyncio.TimeoutError:
            return {
                "eligibility_status": "timeout",
                "error": "Eligibility check timed out",
                "is_eligible": False
            }
        except Exception as e:
            return {
                "eligibility_status": "error",
                "error": str(e),
                "is_eligible": False
            }
    
    def _mock_eligibility_check(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock eligibility check for demonstration"""
        
        member_id = request_data["patient"]["member_id"]
        
        # Simulate different scenarios based on member ID
        if not member_id:
            return {
                "eligibility_status": "failed",
                "error": "Missing member ID",
                "is_eligible": False
            }
        
        # Mock positive eligibility
        if member_id.endswith(("1", "2", "3", "4", "5")):
            return {
                "eligibility_status": "active",
                "is_eligible": True,
                "effective_date": "2024-01-01",
                "termination_date": "2024-12-31",
                "coverage_level": "family",
                "plan_type": "PPO",
                "deductible": {
                    "individual": 1000.00,
                    "family": 2000.00,
                    "remaining": 750.00
                },
                "out_of_pocket_max": {
                    "individual": 5000.00,
                    "family": 10000.00,
                    "remaining": 4200.00
                },
                "copays": {
                    "office_visit": 25.00,
                    "specialist": 50.00,
                    "emergency_room": 200.00,
                    "urgent_care": 75.00
                },
                "coinsurance": 20,  # 20% after deductible
                "benefits": [
                    {
                        "service_type": "medical_care",
                        "coverage_level": "covered",
                        "network_status": "in_network"
                    },
                    {
                        "service_type": "preventive_care",
                        "coverage_level": "covered",
                        "network_status": "in_network",
                        "deductible_applies": False
                    }
                ],
                "checked_date": datetime.now().isoformat()
            }
        
        # Mock inactive eligibility
        elif member_id.endswith(("6", "7")):
            return {
                "eligibility_status": "inactive",
                "is_eligible": False,
                "termination_date": "2023-12-31",
                "termination_reason": "Coverage terminated",
                "checked_date": datetime.now().isoformat()
            }
        
        # Mock pending eligibility
        else:
            return {
                "eligibility_status": "pending",
                "is_eligible": False,
                "pending_reason": "Coverage under review",
                "estimated_resolution": "3-5 business days",
                "checked_date": datetime.now().isoformat()
            }
    
    def _parse_eligibility_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and normalize eligibility response from API"""
        
        # This would parse the actual API response format
        # For now, assume the response is already in our format
        return response


class CoverageVerificationTool(BaseTool):
    """Tool for detailed coverage verification for specific services"""
    
    name: str = "Coverage Verification Tool"
    description: str = (
        "Verify coverage for specific medical services and procedures. "
        "Input should be JSON with patient_info, insurance_info, and service_codes. "
        "Returns detailed coverage information for each service."
    )
    
    def _run(self, input_data: str) -> str:
        """Verify coverage for specific medical services"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            patient_info = data.get("patient_info", {})
            insurance_info = data.get("insurance_info", {})
            service_codes = data.get("service_codes", [])
            service_date = data.get("service_date", datetime.now().date().isoformat())
            
            if not service_codes:
                return json.dumps({
                    "error": "Service codes are required for coverage verification"
                })
            
            # Verify coverage for each service
            coverage_results = []
            
            for service_code in service_codes:
                coverage = self._verify_service_coverage(
                    patient_info, insurance_info, service_code, service_date
                )
                coverage_results.append(coverage)
            
            result = {
                "verification_date": datetime.now().isoformat(),
                "patient_member_id": insurance_info.get("member_id", ""),
                "service_date": service_date,
                "coverage_verifications": coverage_results,
                "overall_status": "verified" if all(c["is_covered"] for c in coverage_results) else "partial"
            }
            
            logger.info(f"Coverage verification completed for {len(service_codes)} services")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Coverage verification failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _verify_service_coverage(self, patient_info: Dict[str, Any], 
                                insurance_info: Dict[str, Any], 
                                service_code: str, 
                                service_date: str) -> Dict[str, Any]:
        """Verify coverage for a specific service code"""
        
        # Mock coverage verification based on service code
        # In production, this would query benefit information
        
        coverage = {
            "service_code": service_code,
            "service_description": self._get_service_description(service_code),
            "is_covered": True,
            "network_status": "in_network",
            "authorization_required": False,
            "coverage_level": "covered",
        }
        
        # Add specific coverage details based on service type
        if service_code.startswith("99"):  # Office visits
            coverage.update({
                "copay": 25.00,
                "deductible_applies": False,
                "coinsurance": 0
            })
        elif service_code.startswith("70"):  # Radiology
            coverage.update({
                "copay": 0,
                "deductible_applies": True,
                "coinsurance": 20,
                "authorization_required": True
            })
        elif service_code.startswith("27"):  # Surgery
            coverage.update({
                "copay": 0,
                "deductible_applies": True,
                "coinsurance": 20,
                "authorization_required": True,
                "precertification_required": True
            })
        else:
            coverage.update({
                "copay": 0,
                "deductible_applies": True,
                "coinsurance": 20
            })
        
        return coverage
    
    def _get_service_description(self, service_code: str) -> str:
        """Get description for service code"""
        
        # Mock service descriptions - in production would query CPT database
        descriptions = {
            "99213": "Office visit, established patient, level 3",
            "99214": "Office visit, established patient, level 4",
            "99203": "Office visit, new patient, level 3",
            "70553": "MRI brain without and with contrast",
            "73721": "MRI knee without contrast",
            "27447": "Total knee arthroplasty",
            "99281": "Emergency department visit, level 1",
            "99285": "Emergency department visit, level 5"
        }
        
        return descriptions.get(service_code, f"Service code {service_code}") 