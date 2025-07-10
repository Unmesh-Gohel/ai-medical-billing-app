"""
Billing and Payment Processing Tools for CrewAI agents
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from crewai_tools import BaseTool
from decimal import Decimal

from app.utils.logging import get_logger
from app.config import settings


logger = get_logger("tools.billing")


class StatementGenerationTool(BaseTool):
    """Tool for generating patient billing statements"""
    
    name: str = "Patient Statement Generator"
    description: str = (
        "Generate patient billing statements with clear itemization and payment options. "
        "Input should be JSON with patient_info, claims, and statement_preferences. "
        "Returns formatted statement ready for delivery."
    )
    
    def _run(self, input_data: str) -> str:
        """Generate patient billing statement"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            patient_info = data.get("patient_info", {})
            claims = data.get("claims", [])
            statement_preferences = data.get("statement_preferences", {})
            
            if not patient_info or not claims:
                return json.dumps({"error": "Patient info and claims are required"})
            
            # Generate statement
            statement = self._generate_statement(patient_info, claims, statement_preferences)
            
            logger.info(f"Statement generated for patient {patient_info.get('patient_id', 'unknown')}")
            return json.dumps(statement, indent=2)
            
        except Exception as e:
            error_msg = f"Statement generation failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _generate_statement(self, patient_info: Dict[str, Any], 
                          claims: List[Dict[str, Any]], 
                          preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive patient statement"""
        
        statement_date = datetime.now().date()
        due_date = statement_date + timedelta(days=30)
        
        # Calculate balances
        total_charges = sum(claim.get("total_charges", 0) for claim in claims)
        insurance_payments = sum(claim.get("insurance_payment", 0) for claim in claims)
        patient_payments = sum(claim.get("patient_payment", 0) for claim in claims)
        adjustments = sum(claim.get("adjustments", 0) for claim in claims)
        
        current_balance = total_charges - insurance_payments - patient_payments - adjustments
        
        # Categorize charges by age
        aged_balances = self._calculate_aged_balances(claims)
        
        # Generate line items
        line_items = []
        for claim in claims:
            line_items.append({
                "service_date": claim.get("service_date"),
                "provider": claim.get("provider_name", "Healthcare Provider"),
                "description": self._get_service_description(claim),
                "charges": claim.get("total_charges", 0),
                "insurance_payment": claim.get("insurance_payment", 0),
                "patient_responsibility": claim.get("patient_responsibility", 0),
                "balance": claim.get("patient_balance", 0)
            })
        
        statement = {
            "statement_id": f"STMT{datetime.now().strftime('%Y%m%d')}{patient_info.get('patient_id', '000')}",
            "statement_date": statement_date.isoformat(),
            "due_date": due_date.isoformat(),
            "patient_info": {
                "name": f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}",
                "address": patient_info.get("address", {}),
                "account_number": patient_info.get("account_number", patient_info.get("patient_id"))
            },
            "summary": {
                "previous_balance": aged_balances.get("previous_balance", 0),
                "charges_this_period": sum(claim.get("total_charges", 0) 
                                         for claim in claims 
                                         if self._is_current_period(claim.get("service_date"))),
                "payments_this_period": sum(claim.get("patient_payment", 0) 
                                          for claim in claims 
                                          if self._is_current_period(claim.get("payment_date"))),
                "adjustments_this_period": sum(claim.get("adjustments", 0) 
                                             for claim in claims 
                                             if self._is_current_period(claim.get("adjustment_date"))),
                "current_balance": current_balance
            },
            "aged_balances": aged_balances,
            "line_items": line_items,
            "payment_options": self._get_payment_options(current_balance, preferences),
            "messages": self._get_statement_messages(current_balance, aged_balances),
            "total_due": max(0, current_balance)
        }
        
        return statement
    
    def _calculate_aged_balances(self, claims: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate aged balance buckets"""
        today = datetime.now().date()
        
        aged_balances = {
            "current": 0.0,      # 0-30 days
            "30_days": 0.0,      # 31-60 days
            "60_days": 0.0,      # 61-90 days
            "90_days": 0.0,      # 91+ days
            "previous_balance": 0.0
        }
        
        for claim in claims:
            service_date_str = claim.get("service_date")
            if not service_date_str:
                continue
            
            try:
                service_date = datetime.strptime(service_date_str, "%Y-%m-%d").date()
                days_old = (today - service_date).days
                balance = claim.get("patient_balance", 0)
                
                if days_old <= 30:
                    aged_balances["current"] += balance
                elif days_old <= 60:
                    aged_balances["30_days"] += balance
                elif days_old <= 90:
                    aged_balances["60_days"] += balance
                else:
                    aged_balances["90_days"] += balance
                    
            except ValueError:
                # If date parsing fails, add to current
                aged_balances["current"] += claim.get("patient_balance", 0)
        
        return aged_balances
    
    def _get_service_description(self, claim: Dict[str, Any]) -> str:
        """Generate service description from claim"""
        procedure_codes = claim.get("procedure_codes", [])
        
        if procedure_codes:
            # Map common procedure codes to descriptions
            descriptions = {
                "99213": "Office Visit - Level 3",
                "99214": "Office Visit - Level 4", 
                "99203": "New Patient Visit - Level 3",
                "96372": "Therapeutic Injection",
                "70553": "MRI Brain",
                "73721": "MRI Knee"
            }
            
            primary_code = procedure_codes[0] if procedure_codes else ""
            description = descriptions.get(primary_code, f"Medical Service ({primary_code})")
            
            if len(procedure_codes) > 1:
                description += f" and {len(procedure_codes) - 1} other service(s)"
                
            return description
        
        return "Medical Services"
    
    def _is_current_period(self, date_str: Optional[str]) -> bool:
        """Check if date is in current billing period (last 30 days)"""
        if not date_str:
            return False
            
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            days_ago = (datetime.now().date() - date_obj).days
            return 0 <= days_ago <= 30
        except (ValueError, TypeError):
            return False
    
    def _get_payment_options(self, balance: float, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate payment options based on balance and preferences"""
        payment_options = {
            "online_portal": {
                "available": True,
                "url": preferences.get("portal_url", "https://portal.healthcare.com"),
                "accepted_methods": ["credit_card", "bank_transfer", "paypal"]
            },
            "phone": {
                "available": True,
                "number": preferences.get("payment_phone", "(555) 123-4567"),
                "hours": "Monday-Friday 8:00 AM - 6:00 PM"
            },
            "mail": {
                "available": True,
                "address": preferences.get("payment_address", "PO Box 1234, City, ST 12345"),
                "make_check_payable": preferences.get("payee_name", "Healthcare Provider")
            }
        }
        
        # Add payment plan option for larger balances
        if balance > 500:
            payment_options["payment_plan"] = {
                "available": True,
                "minimum_monthly": max(25, balance / 12),
                "contact_info": "Call (555) 123-4567 to set up a payment plan"
            }
        
        return payment_options
    
    def _get_statement_messages(self, balance: float, aged_balances: Dict[str, float]) -> List[str]:
        """Generate contextual messages for the statement"""
        messages = []
        
        if balance <= 0:
            messages.append("Thank you! Your account is current.")
        elif aged_balances.get("90_days", 0) > 0:
            messages.append("IMPORTANT: Your account has charges over 90 days old. Please contact us immediately to avoid collection actions.")
        elif aged_balances.get("60_days", 0) > 0:
            messages.append("Your account has charges over 60 days old. Please remit payment or contact us to discuss payment arrangements.")
        elif balance > 1000:
            messages.append("Payment plans are available for balances over $500. Call us to discuss options.")
        else:
            messages.append("Thank you for choosing our healthcare services.")
        
        # Add insurance information if applicable
        if any(aged_balances.get(period, 0) > 0 for period in ["30_days", "60_days", "90_days"]):
            messages.append("If you have questions about insurance coverage, please contact your insurance company.")
        
        return messages


class PaymentProcessingTool(BaseTool):
    """Tool for processing patient payments"""
    
    name: str = "Payment Processor"
    description: str = (
        "Process patient payments through various methods including credit cards, ACH, and payment plans. "
        "Input should be JSON with payment_info and processing_options. "
        "Returns payment confirmation and receipt information."
    )
    
    def _run(self, input_data: str) -> str:
        """Process patient payment"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            payment_info = data.get("payment_info", {})
            processing_options = data.get("processing_options", {})
            
            if not payment_info:
                return json.dumps({"error": "Payment information is required"})
            
            # Process payment
            payment_result = self._process_payment(payment_info, processing_options)
            
            logger.info(f"Payment processed: {payment_result.get('transaction_id', 'unknown')}")
            return json.dumps(payment_result, indent=2)
            
        except Exception as e:
            error_msg = f"Payment processing failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _process_payment(self, payment_info: Dict[str, Any], 
                        options: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through appropriate gateway"""
        
        payment_method = payment_info.get("payment_method", "credit_card")
        amount = payment_info.get("amount", 0.0)
        
        # Generate transaction ID
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Mock payment processing - in production would integrate with actual gateway
        if settings.PAYMENT_GATEWAY_URL:
            return self._real_payment_processing(payment_info, transaction_id)
        else:
            return self._mock_payment_processing(payment_info, transaction_id)
    
    def _real_payment_processing(self, payment_info: Dict[str, Any], transaction_id: str) -> Dict[str, Any]:
        """Process payment through real gateway"""
        # This would integrate with Stripe, Square, or healthcare-specific gateway
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": payment_info.get("amount", 0.0),
            "payment_method": payment_info.get("payment_method"),
            "processed_at": datetime.now().isoformat(),
            "gateway": "Production Gateway"
        }
    
    def _mock_payment_processing(self, payment_info: Dict[str, Any], transaction_id: str) -> Dict[str, Any]:
        """Mock payment processing for demonstration"""
        
        amount = payment_info.get("amount", 0.0)
        payment_method = payment_info.get("payment_method", "credit_card")
        
        # Simulate different outcomes based on amount
        if amount <= 0:
            return {
                "status": "failed",
                "error": "Invalid payment amount",
                "transaction_id": transaction_id
            }
        elif amount > 10000:
            return {
                "status": "failed", 
                "error": "Amount exceeds daily limit",
                "transaction_id": transaction_id
            }
        else:
            return {
                "status": "success",
                "transaction_id": transaction_id,
                "amount": amount,
                "payment_method": payment_method,
                "processed_at": datetime.now().isoformat(),
                "confirmation_number": f"CONF{transaction_id[-8:]}",
                "receipt": {
                    "transaction_id": transaction_id,
                    "amount": f"${amount:.2f}",
                    "payment_method": payment_method.replace("_", " ").title(),
                    "date": datetime.now().strftime("%B %d, %Y"),
                    "time": datetime.now().strftime("%I:%M %p")
                },
                "gateway": "Mock Payment Gateway"
            } 