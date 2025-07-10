"""
Communication and Collaboration Tools for CrewAI agents
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from crewai_tools import BaseTool

from app.utils.logging import get_logger


logger = get_logger("tools.communication")


class PatientCommunicationTool(BaseTool):
    """Tool for patient communications including emails, SMS, and letters"""
    
    name: str = "Patient Communication System"
    description: str = (
        "Send communications to patients via email, SMS, or mail including appointment reminders, "
        "billing statements, and educational materials. Input should be JSON with recipient_info, "
        "message_type, and content_data. Returns delivery confirmation and tracking information."
    )
    
    def _run(self, input_data: str) -> str:
        """Send patient communication"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            recipient_info = data.get("recipient_info", {})
            message_type = data.get("message_type", "general")
            content_data = data.get("content_data", {})
            delivery_method = data.get("delivery_method", "email")
            
            if not recipient_info:
                return json.dumps({"error": "Recipient information is required"})
            
            # Send communication
            result = self._send_communication(recipient_info, message_type, content_data, delivery_method)
            
            logger.info(f"Communication sent: {message_type} to {recipient_info.get('patient_id', 'unknown')}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Communication sending failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _send_communication(self, recipient_info: Dict[str, Any], message_type: str,
                          content_data: Dict[str, Any], delivery_method: str) -> Dict[str, Any]:
        """Send communication through specified method"""
        
        # Generate message content based on type
        content = self._generate_message_content(message_type, content_data, recipient_info)
        
        # Generate tracking ID
        tracking_id = f"COMM{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Mock delivery - in production would integrate with actual communication services
        delivery_result = self._mock_delivery(recipient_info, content, delivery_method, tracking_id)
        
        return {
            "tracking_id": tracking_id,
            "message_type": message_type,
            "delivery_method": delivery_method,
            "recipient": recipient_info.get("patient_name", "Unknown"),
            "sent_at": datetime.now().isoformat(),
            "delivery_status": delivery_result.get("status", "pending"),
            "content_preview": content.get("subject", "")[:50] + "...",
            "delivery_details": delivery_result
        }
    
    def _generate_message_content(self, message_type: str, content_data: Dict[str, Any],
                                recipient_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate message content based on type and data"""
        
        patient_name = recipient_info.get("patient_name", "Patient")
        
        if message_type == "appointment_reminder":
            return self._generate_appointment_reminder(content_data, patient_name)
        elif message_type == "billing_statement":
            return self._generate_billing_communication(content_data, patient_name)
        elif message_type == "insurance_update":
            return self._generate_insurance_update(content_data, patient_name)
        elif message_type == "payment_reminder":
            return self._generate_payment_reminder(content_data, patient_name)
        elif message_type == "educational":
            return self._generate_educational_content(content_data, patient_name)
        else:
            return self._generate_general_communication(content_data, patient_name)
    
    def _generate_appointment_reminder(self, content_data: Dict[str, Any], patient_name: str) -> Dict[str, Any]:
        """Generate appointment reminder content"""
        
        appointment_date = content_data.get("appointment_date", "")
        appointment_time = content_data.get("appointment_time", "")
        provider_name = content_data.get("provider_name", "your healthcare provider")
        location = content_data.get("location", "our clinic")
        
        return {
            "subject": f"Appointment Reminder - {appointment_date}",
            "body": f"""
Dear {patient_name},

This is a reminder of your upcoming appointment:

Date: {appointment_date}
Time: {appointment_time}
Provider: {provider_name}
Location: {location}

Please arrive 15 minutes early to complete any necessary paperwork. 

If you need to reschedule, please call us at least 24 hours in advance.

Contact us: (555) 123-4567

Thank you,
Healthcare Team
            """.strip(),
            "type": "appointment_reminder"
        }
    
    def _generate_billing_communication(self, content_data: Dict[str, Any], patient_name: str) -> Dict[str, Any]:
        """Generate billing-related communication"""
        
        amount_due = content_data.get("amount_due", 0.0)
        due_date = content_data.get("due_date", "")
        account_number = content_data.get("account_number", "")
        
        return {
            "subject": f"Billing Statement - Account {account_number}",
            "body": f"""
Dear {patient_name},

Your billing statement is ready for review.

Account Number: {account_number}
Amount Due: ${amount_due:.2f}
Due Date: {due_date}

You can view your full statement and make payments online at our patient portal.

Payment Options:
- Online: www.healthcareportal.com
- Phone: (555) 123-4567
- Mail: Include account number with payment

If you have questions about your bill, please contact our billing department.

Thank you,
Billing Department
            """.strip(),
            "type": "billing_statement"
        }
    
    def _generate_payment_reminder(self, content_data: Dict[str, Any], patient_name: str) -> Dict[str, Any]:
        """Generate payment reminder content"""
        
        amount_due = content_data.get("amount_due", 0.0)
        days_overdue = content_data.get("days_overdue", 0)
        account_number = content_data.get("account_number", "")
        
        urgency_level = "urgent" if days_overdue > 60 else "standard"
        
        return {
            "subject": f"Payment Reminder - Account {account_number}",
            "body": f"""
Dear {patient_name},

This is a {"URGENT " if urgency_level == "urgent" else ""}payment reminder for your account.

Account Number: {account_number}
Amount Due: ${amount_due:.2f}
Days Past Due: {days_overdue}

Please remit payment immediately to avoid any collection actions.

Payment Options:
- Online: www.healthcareportal.com
- Phone: (555) 123-4567
- Payment plans available for qualifying accounts

Contact our billing department to discuss payment arrangements: (555) 123-4567

Thank you,
Billing Department
            """.strip(),
            "type": "payment_reminder"
        }
    
    def _generate_insurance_update(self, content_data: Dict[str, Any], patient_name: str) -> Dict[str, Any]:
        """Generate insurance update communication"""
        
        update_type = content_data.get("update_type", "general")
        insurance_company = content_data.get("insurance_company", "your insurance")
        
        return {
            "subject": f"Insurance Update Required - {insurance_company}",
            "body": f"""
Dear {patient_name},

We need updated insurance information for your account.

Current Issue: {update_type}
Insurance Company: {insurance_company}

Please provide:
- Updated insurance card (front and back)
- Current policy information
- Authorization forms if required

You can submit this information:
- Through our patient portal
- By calling (555) 123-4567
- By bringing to your next appointment

Prompt submission helps ensure timely processing of your claims.

Thank you,
Insurance Verification Team
            """.strip(),
            "type": "insurance_update"
        }
    
    def _generate_educational_content(self, content_data: Dict[str, Any], patient_name: str) -> Dict[str, Any]:
        """Generate educational content"""
        
        topic = content_data.get("topic", "Healthcare")
        resources = content_data.get("resources", [])
        
        return {
            "subject": f"Health Education: {topic}",
            "body": f"""
Dear {patient_name},

We're sharing some educational information about {topic} that may be helpful for your health journey.

Key Points:
- Follow your provider's recommendations
- Take medications as prescribed
- Schedule regular follow-up appointments
- Contact us with any questions

Additional Resources:
{chr(10).join(f"- {resource}" for resource in resources)}

If you have questions about this information, please discuss with your provider at your next visit.

Stay healthy,
Your Healthcare Team
            """.strip(),
            "type": "educational"
        }
    
    def _generate_general_communication(self, content_data: Dict[str, Any], patient_name: str) -> Dict[str, Any]:
        """Generate general communication"""
        
        subject = content_data.get("subject", "Healthcare Communication")
        message = content_data.get("message", "Thank you for choosing our healthcare services.")
        
        return {
            "subject": subject,
            "body": f"""
Dear {patient_name},

{message}

If you have any questions, please don't hesitate to contact us at (555) 123-4567.

Thank you,
Healthcare Team
            """.strip(),
            "type": "general"
        }
    
    def _mock_delivery(self, recipient_info: Dict[str, Any], content: Dict[str, Any],
                      delivery_method: str, tracking_id: str) -> Dict[str, Any]:
        """Mock communication delivery"""
        
        # Simulate delivery based on method
        if delivery_method == "email":
            return {
                "status": "delivered",
                "delivery_time": datetime.now().isoformat(),
                "recipient_email": recipient_info.get("email", "patient@example.com"),
                "delivery_method": "email",
                "tracking_id": tracking_id
            }
        elif delivery_method == "sms":
            return {
                "status": "delivered",
                "delivery_time": datetime.now().isoformat(),
                "recipient_phone": recipient_info.get("phone", "(555) 123-4567"),
                "delivery_method": "sms",
                "tracking_id": tracking_id
            }
        elif delivery_method == "mail":
            return {
                "status": "processed",
                "estimated_delivery": (datetime.now() + timedelta(days=3)).date().isoformat(),
                "recipient_address": recipient_info.get("address", "123 Main St"),
                "delivery_method": "mail",
                "tracking_id": tracking_id
            }
        else:
            return {
                "status": "failed",
                "error": f"Unsupported delivery method: {delivery_method}",
                "tracking_id": tracking_id
            }


class TeamCollaborationTool(BaseTool):
    """Tool for internal team communications and task coordination"""
    
    name: str = "Team Collaboration System"
    description: str = (
        "Facilitate internal team communications, task assignments, and workflow coordination. "
        "Input should be JSON with collaboration_type, participants, and task_data. "
        "Returns collaboration confirmation and tracking information."
    )
    
    def _run(self, input_data: str) -> str:
        """Coordinate team collaboration"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            collaboration_type = data.get("collaboration_type", "task_assignment")
            participants = data.get("participants", [])
            task_data = data.get("task_data", {})
            
            if not participants:
                return json.dumps({"error": "Participants are required"})
            
            # Process collaboration
            result = self._process_collaboration(collaboration_type, participants, task_data)
            
            logger.info(f"Team collaboration initiated: {collaboration_type}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Team collaboration failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _process_collaboration(self, collaboration_type: str, participants: List[str],
                             task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process team collaboration request"""
        
        collaboration_id = f"COLLAB{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if collaboration_type == "task_assignment":
            return self._assign_task(participants, task_data, collaboration_id)
        elif collaboration_type == "workflow_escalation":
            return self._escalate_workflow(participants, task_data, collaboration_id)
        elif collaboration_type == "case_review":
            return self._initiate_case_review(participants, task_data, collaboration_id)
        elif collaboration_type == "knowledge_sharing":
            return self._share_knowledge(participants, task_data, collaboration_id)
        else:
            return {"error": f"Unknown collaboration type: {collaboration_type}"}
    
    def _assign_task(self, participants: List[str], task_data: Dict[str, Any],
                    collaboration_id: str) -> Dict[str, Any]:
        """Assign task to team members"""
        
        task_title = task_data.get("title", "New Task")
        priority = task_data.get("priority", "medium")
        due_date = task_data.get("due_date", (datetime.now() + timedelta(days=3)).date().isoformat())
        
        return {
            "collaboration_id": collaboration_id,
            "type": "task_assignment",
            "task": {
                "title": task_title,
                "priority": priority,
                "due_date": due_date,
                "assigned_to": participants,
                "status": "assigned",
                "created_at": datetime.now().isoformat()
            },
            "notifications_sent": len(participants),
            "tracking_url": f"https://internal.healthcare.com/tasks/{collaboration_id}"
        }
    
    def _escalate_workflow(self, participants: List[str], task_data: Dict[str, Any],
                          collaboration_id: str) -> Dict[str, Any]:
        """Escalate workflow to supervisors"""
        
        issue_type = task_data.get("issue_type", "general")
        severity = task_data.get("severity", "medium")
        patient_id = task_data.get("patient_id", "")
        
        return {
            "collaboration_id": collaboration_id,
            "type": "workflow_escalation",
            "escalation": {
                "issue_type": issue_type,
                "severity": severity,
                "patient_id": patient_id,
                "escalated_to": participants,
                "escalated_at": datetime.now().isoformat(),
                "status": "pending_review"
            },
            "response_required": True,
            "sla_deadline": (datetime.now() + timedelta(hours=4)).isoformat()
        }
    
    def _initiate_case_review(self, participants: List[str], task_data: Dict[str, Any],
                            collaboration_id: str) -> Dict[str, Any]:
        """Initiate case review meeting"""
        
        patient_id = task_data.get("patient_id", "")
        review_type = task_data.get("review_type", "complex_case")
        
        return {
            "collaboration_id": collaboration_id,
            "type": "case_review",
            "review": {
                "patient_id": patient_id,
                "review_type": review_type,
                "participants": participants,
                "scheduled_for": (datetime.now() + timedelta(days=1)).isoformat(),
                "status": "scheduled",
                "agenda": [
                    "Review patient history",
                    "Discuss treatment options",
                    "Coordinate care plan",
                    "Address billing questions"
                ]
            },
            "meeting_link": f"https://meet.healthcare.com/{collaboration_id}"
        }
    
    def _share_knowledge(self, participants: List[str], task_data: Dict[str, Any],
                        collaboration_id: str) -> Dict[str, Any]:
        """Share knowledge or best practices"""
        
        knowledge_type = task_data.get("knowledge_type", "best_practice")
        topic = task_data.get("topic", "Healthcare Process")
        
        return {
            "collaboration_id": collaboration_id,
            "type": "knowledge_sharing",
            "knowledge": {
                "type": knowledge_type,
                "topic": topic,
                "shared_with": participants,
                "shared_at": datetime.now().isoformat(),
                "status": "shared"
            },
            "access_link": f"https://knowledge.healthcare.com/{collaboration_id}"
        } 