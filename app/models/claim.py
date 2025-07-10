"""
Claim models for managing medical claims, claim lines, statuses, and denials
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, Enum, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum

from app.models.base import BaseModel, AuditMixin, generate_claim_number


class ClaimType(enum.Enum):
    PROFESSIONAL = "professional"  # CMS-1500
    INSTITUTIONAL = "institutional"  # UB-04
    DENTAL = "dental"
    VISION = "vision"
    PHARMACY = "pharmacy"


class ClaimStatus(enum.Enum):
    DRAFT = "draft"
    READY_TO_SUBMIT = "ready_to_submit"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DENIED = "denied"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    APPEALED = "appealed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ClaimPriority(enum.Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class Claim(BaseModel, AuditMixin):
    """Medical claim model"""
    
    __tablename__ = "claims"
    
    # Claim identification
    claim_number = Column(String(20), unique=True, nullable=False, default=generate_claim_number)
    external_claim_id = Column(String(50), nullable=True)  # Payer's claim ID
    
    # Patient and provider information
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    
    # Claim details
    claim_type = Column(Enum(ClaimType), nullable=False)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.DRAFT, nullable=False)
    priority = Column(Enum(ClaimPriority), default=ClaimPriority.ROUTINE, nullable=False)
    
    # Service dates
    service_date_from = Column(Date, nullable=False)
    service_date_to = Column(Date, nullable=True)
    
    # Financial information
    total_charges = Column(Numeric(10, 2), nullable=False, default=0)
    total_allowed = Column(Numeric(10, 2), nullable=True)
    total_paid = Column(Numeric(10, 2), nullable=True, default=0)
    total_patient_responsibility = Column(Numeric(10, 2), nullable=True, default=0)
    total_adjustments = Column(Numeric(10, 2), nullable=True, default=0)
    
    # Insurance information
    primary_insurance_id = Column(Integer, ForeignKey("patient_insurance.id"), nullable=True)
    secondary_insurance_id = Column(Integer, ForeignKey("patient_insurance.id"), nullable=True)
    
    # Submission information
    submitted_date = Column(DateTime, nullable=True)
    submitted_by = Column(String(100), nullable=True)
    clearinghouse = Column(String(100), nullable=True)
    
    # Processing information
    processed_date = Column(DateTime, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    
    # Additional information
    diagnosis_codes = Column(Text, nullable=True)  # JSON array of ICD codes
    place_of_service = Column(String(10), nullable=True)
    claim_frequency = Column(String(1), nullable=True)  # 1=original, 7=replacement, 8=void
    
    # Notes and comments
    notes = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="claims")
    claim_lines = relationship("ClaimLine", back_populates="claim", cascade="all, delete-orphan")
    claim_statuses = relationship("ClaimStatusHistory", back_populates="claim", cascade="all, delete-orphan")
    denials = relationship("ClaimDenial", back_populates="claim", cascade="all, delete-orphan")
    primary_insurance = relationship("PatientInsurance", foreign_keys=[primary_insurance_id])
    secondary_insurance = relationship("PatientInsurance", foreign_keys=[secondary_insurance_id])
    
    @hybrid_property
    def days_in_ar(self) -> int:
        """Calculate days in accounts receivable"""
        if self.status == ClaimStatus.PAID:
            return 0
        
        start_date = self.submitted_date.date() if self.submitted_date else self.service_date_from
        return (date.today() - start_date).days
    
    @hybrid_property
    def outstanding_balance(self) -> Optional[float]:
        """Calculate outstanding balance"""
        if self.total_charges is None:
            return None
        
        paid = float(self.total_paid) if self.total_paid else 0
        adjustments = float(self.total_adjustments) if self.total_adjustments else 0
        
        return float(self.total_charges) - paid - adjustments
    
    @hybrid_property
    def is_clean_claim(self) -> bool:
        """Check if claim is clean (no errors or issues)"""
        return len(self.denials) == 0 and self.status not in [ClaimStatus.REJECTED, ClaimStatus.DENIED]
    
    def get_primary_diagnosis(self) -> Optional[str]:
        """Get primary diagnosis code"""
        if self.diagnosis_codes:
            import json
            try:
                codes = json.loads(self.diagnosis_codes)
                return codes[0] if codes else None
            except (json.JSONDecodeError, IndexError):
                return None
        return None
    
    def add_status_history(self, status: ClaimStatus, notes: str = None, user_id: str = None):
        """Add status history entry"""
        status_history = ClaimStatusHistory(
            claim_id=self.id,
            status=status,
            notes=notes,
            changed_by=user_id,
            changed_date=datetime.utcnow()
        )
        self.claim_statuses.append(status_history)
        self.status = status
        return status_history
    
    def __repr__(self):
        return f"<Claim(claim_number='{self.claim_number}', patient_id={self.patient_id}, status='{self.status}')>"


class ClaimLine(BaseModel):
    """Individual line items on a claim"""
    
    __tablename__ = "claim_lines"
    
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Procedure information
    procedure_code = Column(String(20), nullable=False)  # CPT/HCPCS code
    procedure_description = Column(String(200), nullable=True)
    modifier_1 = Column(String(2), nullable=True)
    modifier_2 = Column(String(2), nullable=True)
    modifier_3 = Column(String(2), nullable=True)
    modifier_4 = Column(String(2), nullable=True)
    
    # Diagnosis pointer
    diagnosis_pointer = Column(String(10), nullable=True)  # Points to diagnosis codes
    
    # Service details
    service_date = Column(Date, nullable=False)
    units = Column(Integer, default=1, nullable=False)
    
    # Financial information
    charges = Column(Numeric(10, 2), nullable=False)
    allowed_amount = Column(Numeric(10, 2), nullable=True)
    paid_amount = Column(Numeric(10, 2), nullable=True, default=0)
    patient_responsibility = Column(Numeric(10, 2), nullable=True, default=0)
    adjustment_amount = Column(Numeric(10, 2), nullable=True, default=0)
    
    # Revenue code (for institutional claims)
    revenue_code = Column(String(10), nullable=True)
    
    # NDC information (for drugs)
    ndc_code = Column(String(20), nullable=True)
    ndc_units = Column(Numeric(10, 3), nullable=True)
    ndc_unit_measure = Column(String(10), nullable=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="claim_lines")
    
    @hybrid_property
    def outstanding_balance(self) -> float:
        """Calculate outstanding balance for this line"""
        paid = float(self.paid_amount) if self.paid_amount else 0
        adjustments = float(self.adjustment_amount) if self.adjustment_amount else 0
        return float(self.charges) - paid - adjustments
    
    def __repr__(self):
        return f"<ClaimLine(claim_id={self.claim_id}, line={self.line_number}, code='{self.procedure_code}')>"


class ClaimStatusHistory(BaseModel):
    """History of claim status changes"""
    
    __tablename__ = "claim_status_history"
    
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    status = Column(Enum(ClaimStatus), nullable=False)
    changed_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    changed_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="claim_statuses")
    
    def __repr__(self):
        return f"<ClaimStatusHistory(claim_id={self.claim_id}, status='{self.status}', date={self.changed_date})>"


class DenialCategory(enum.Enum):
    AUTHORIZATION = "authorization"
    CODING = "coding"
    ELIGIBILITY = "eligibility"
    MEDICAL_NECESSITY = "medical_necessity"
    DUPLICATE = "duplicate"
    TIMELY_FILING = "timely_filing"
    MISSING_INFORMATION = "missing_information"
    COORDINATION_OF_BENEFITS = "coordination_of_benefits"
    OTHER = "other"


class ClaimDenial(BaseModel):
    """Claim denial information"""
    
    __tablename__ = "claim_denials"
    
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    claim_line_id = Column(Integer, ForeignKey("claim_lines.id"), nullable=True)
    
    # Denial details
    denial_code = Column(String(20), nullable=False)
    denial_description = Column(Text, nullable=True)
    denial_category = Column(Enum(DenialCategory), nullable=True)
    
    # Amounts
    denied_amount = Column(Numeric(10, 2), nullable=False)
    
    # Dates
    denial_date = Column(Date, nullable=False)
    appeal_deadline = Column(Date, nullable=True)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text, nullable=True)
    resolved_date = Column(Date, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    
    # Appeal information
    appeal_filed = Column(Boolean, default=False)
    appeal_date = Column(Date, nullable=True)
    appeal_outcome = Column(String(20), nullable=True)  # approved, denied, partial
    
    # Relationships
    claim = relationship("Claim", back_populates="denials")
    claim_line = relationship("ClaimLine")
    
    @hybrid_property
    def days_to_appeal_deadline(self) -> Optional[int]:
        """Calculate days until appeal deadline"""
        if not self.appeal_deadline:
            return None
        
        return (self.appeal_deadline - date.today()).days
    
    @hybrid_property
    def is_appeal_overdue(self) -> bool:
        """Check if appeal deadline has passed"""
        if not self.appeal_deadline:
            return False
        
        return date.today() > self.appeal_deadline
    
    def __repr__(self):
        return f"<ClaimDenial(claim_id={self.claim_id}, code='{self.denial_code}', amount={self.denied_amount})>" 