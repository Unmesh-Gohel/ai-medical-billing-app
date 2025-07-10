"""
Database Tools for CrewAI agents to access patient, claim, and insurance data
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from crewai_tools import BaseTool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.utils.logging import get_logger
from app.config import settings
from app.models.patient import Patient
from app.models.claim import Claim, Insurance


logger = get_logger("tools.database")


class PatientLookupTool(BaseTool):
    """Tool for looking up patient information"""
    
    name: str = "Patient Database Lookup"
    description: str = (
        "Look up patient information from the database. "
        "Input should be patient ID, name, or other identifying information. "
        "Returns patient demographics and insurance information."
    )
    
    def _run(self, search_criteria: str) -> str:
        """Look up patient information"""
        try:
            # Parse search criteria
            if isinstance(search_criteria, str):
                try:
                    criteria = json.loads(search_criteria)
                except:
                    # If not JSON, treat as patient ID
                    criteria = {"patient_id": search_criteria}
            else:
                criteria = search_criteria
            
            # Mock patient lookup - in production would query actual database
            patient_data = self._mock_patient_lookup(criteria)
            
            logger.info(f"Patient lookup completed for criteria: {criteria}")
            return json.dumps(patient_data, indent=2)
            
        except Exception as e:
            error_msg = f"Patient lookup failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _mock_patient_lookup(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Mock patient lookup for demonstration"""
        
        patient_id = criteria.get("patient_id")
        
        # Mock patient database
        patients = {
            "P001": {
                "patient_id": "P001",
                "first_name": "John",
                "last_name": "Smith",
                "date_of_birth": "1980-05-15",
                "gender": "M",
                "ssn": "***-**-1234",
                "phone": "(555) 123-4567",
                "email": "john.smith@email.com",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip_code": "90210"
                },
                "insurance": {
                    "primary": {
                        "insurance_id": "INS001",
                        "member_id": "MB123456789",
                        "payer_name": "Blue Cross Blue Shield",
                        "group_number": "GRP001",
                        "effective_date": "2024-01-01",
                        "termination_date": "2024-12-31"
                    }
                },
                "emergency_contact": {
                    "name": "Jane Smith",
                    "relationship": "Spouse",
                    "phone": "(555) 123-4568"
                }
            },
            "P002": {
                "patient_id": "P002", 
                "first_name": "Mary",
                "last_name": "Johnson",
                "date_of_birth": "1975-09-22",
                "gender": "F",
                "ssn": "***-**-5678",
                "phone": "(555) 987-6543",
                "email": "mary.johnson@email.com",
                "address": {
                    "street": "456 Oak Ave",
                    "city": "Springfield",
                    "state": "NY",
                    "zip_code": "12345"
                },
                "insurance": {
                    "primary": {
                        "insurance_id": "INS002",
                        "member_id": "MB987654321",
                        "payer_name": "Aetna",
                        "group_number": "GRP002",
                        "effective_date": "2024-01-01",
                        "termination_date": "2024-12-31"
                    }
                }
            }
        }
        
        if patient_id and patient_id in patients:
            return {
                "found": True,
                "patient": patients[patient_id],
                "lookup_date": datetime.now().isoformat()
            }
        
        # Search by name if patient_id not found
        first_name = criteria.get("first_name", "").lower()
        last_name = criteria.get("last_name", "").lower()
        
        if first_name and last_name:
            for patient in patients.values():
                if (patient["first_name"].lower() == first_name and 
                    patient["last_name"].lower() == last_name):
                    return {
                        "found": True,
                        "patient": patient,
                        "lookup_date": datetime.now().isoformat()
                    }
        
        return {
            "found": False,
            "message": "Patient not found",
            "lookup_date": datetime.now().isoformat()
        }


class ClaimLookupTool(BaseTool):
    """Tool for looking up claim information"""
    
    name: str = "Claim Database Lookup"
    description: str = (
        "Look up claim information from the database. "
        "Input should be claim ID, patient ID, or date range. "
        "Returns claim details, status, and payment information."
    )
    
    def _run(self, search_criteria: str) -> str:
        """Look up claim information"""
        try:
            # Parse search criteria
            if isinstance(search_criteria, str):
                try:
                    criteria = json.loads(search_criteria)
                except:
                    # If not JSON, treat as claim ID
                    criteria = {"claim_id": search_criteria}
            else:
                criteria = search_criteria
            
            # Mock claim lookup
            claim_data = self._mock_claim_lookup(criteria)
            
            logger.info(f"Claim lookup completed for criteria: {criteria}")
            return json.dumps(claim_data, indent=2)
            
        except Exception as e:
            error_msg = f"Claim lookup failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _mock_claim_lookup(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Mock claim lookup for demonstration"""
        
        claim_id = criteria.get("claim_id")
        patient_id = criteria.get("patient_id")
        
        # Mock claims database
        claims = {
            "CLM001": {
                "claim_id": "CLM001",
                "patient_id": "P001",
                "service_date": "2024-01-15",
                "provider_id": "PRV001",
                "diagnosis_codes": ["E11.9", "I10"],
                "procedure_codes": ["99213", "96372"],
                "total_charges": 275.00,
                "status": "paid",
                "payment_amount": 220.00,
                "payment_date": "2024-02-15",
                "insurance": {
                    "payer_name": "Blue Cross Blue Shield",
                    "member_id": "MB123456789"
                }
            },
            "CLM002": {
                "claim_id": "CLM002",
                "patient_id": "P001",
                "service_date": "2024-02-01",
                "provider_id": "PRV001",
                "diagnosis_codes": ["Z00.00"],
                "procedure_codes": ["99214"],
                "total_charges": 185.00,
                "status": "pending",
                "submitted_date": "2024-02-02",
                "insurance": {
                    "payer_name": "Blue Cross Blue Shield",
                    "member_id": "MB123456789"
                }
            }
        }
        
        if claim_id and claim_id in claims:
            return {
                "found": True,
                "claim": claims[claim_id],
                "lookup_date": datetime.now().isoformat()
            }
        
        # Search by patient ID
        if patient_id:
            patient_claims = [claim for claim in claims.values() 
                            if claim["patient_id"] == patient_id]
            
            if patient_claims:
                return {
                    "found": True,
                    "claims": patient_claims,
                    "count": len(patient_claims),
                    "lookup_date": datetime.now().isoformat()
                }
        
        return {
            "found": False,
            "message": "No claims found",
            "lookup_date": datetime.now().isoformat()
        }


class InsuranceLookupTool(BaseTool):
    """Tool for looking up insurance information"""
    
    name: str = "Insurance Database Lookup"
    description: str = (
        "Look up insurance information from the database. "
        "Input should be insurance ID, member ID, or payer name. "
        "Returns insurance details, coverage, and benefit information."
    )
    
    def _run(self, search_criteria: str) -> str:
        """Look up insurance information"""
        try:
            # Parse search criteria
            if isinstance(search_criteria, str):
                try:
                    criteria = json.loads(search_criteria)
                except:
                    # If not JSON, treat as member ID
                    criteria = {"member_id": search_criteria}
            else:
                criteria = search_criteria
            
            # Mock insurance lookup
            insurance_data = self._mock_insurance_lookup(criteria)
            
            logger.info(f"Insurance lookup completed for criteria: {criteria}")
            return json.dumps(insurance_data, indent=2)
            
        except Exception as e:
            error_msg = f"Insurance lookup failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _mock_insurance_lookup(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Mock insurance lookup for demonstration"""
        
        member_id = criteria.get("member_id")
        insurance_id = criteria.get("insurance_id")
        
        # Mock insurance database
        insurance_plans = {
            "INS001": {
                "insurance_id": "INS001",
                "member_id": "MB123456789",
                "payer_name": "Blue Cross Blue Shield",
                "payer_id": "60054",
                "plan_name": "PPO Gold",
                "group_number": "GRP001",
                "effective_date": "2024-01-01",
                "termination_date": "2024-12-31",
                "coverage_type": "medical",
                "benefits": {
                    "deductible": {
                        "individual": 1000.00,
                        "family": 2000.00
                    },
                    "out_of_pocket_max": {
                        "individual": 5000.00,
                        "family": 10000.00
                    },
                    "office_visit_copay": 25.00,
                    "specialist_copay": 50.00,
                    "coinsurance": 20
                },
                "status": "active"
            },
            "INS002": {
                "insurance_id": "INS002",
                "member_id": "MB987654321",
                "payer_name": "Aetna",
                "payer_id": "60054",
                "plan_name": "HMO Select",
                "group_number": "GRP002",
                "effective_date": "2024-01-01",
                "termination_date": "2024-12-31",
                "coverage_type": "medical",
                "benefits": {
                    "deductible": {
                        "individual": 500.00,
                        "family": 1500.00
                    },
                    "out_of_pocket_max": {
                        "individual": 3000.00,
                        "family": 6000.00
                    },
                    "office_visit_copay": 20.00,
                    "specialist_copay": 40.00,
                    "coinsurance": 10
                },
                "status": "active"
            }
        }
        
        if insurance_id and insurance_id in insurance_plans:
            return {
                "found": True,
                "insurance": insurance_plans[insurance_id],
                "lookup_date": datetime.now().isoformat()
            }
        
        # Search by member ID
        if member_id:
            for insurance in insurance_plans.values():
                if insurance["member_id"] == member_id:
                    return {
                        "found": True,
                        "insurance": insurance,
                        "lookup_date": datetime.now().isoformat()
                    }
        
        return {
            "found": False,
            "message": "Insurance information not found",
            "lookup_date": datetime.now().isoformat()
        } 