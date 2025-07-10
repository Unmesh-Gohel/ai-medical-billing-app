"""
Patient model with encrypted PHI fields and insurance information
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum

from app.models.base import BaseModel, AuditMixin, EncryptedField, generate_medical_record_number


class Gender(enum.Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    UNKNOWN = "U"


class MaritalStatus(enum.Enum):
    SINGLE = "S"
    MARRIED = "M"
    DIVORCED = "D"
    WIDOWED = "W"
    SEPARATED = "P"
    UNKNOWN = "U"


class Patient(BaseModel, AuditMixin):
    """Patient model with encrypted PHI fields"""
    
    __tablename__ = "patients"
    
    # Medical Record Number - unique identifier
    medical_record_number = Column(String(20), unique=True, nullable=False, 
                                  default=generate_medical_record_number)
    
    # Encrypted PHI fields
    first_name_encrypted = Column(Text, nullable=False)
    last_name_encrypted = Column(Text, nullable=False)
    middle_name_encrypted = Column(Text, nullable=True)
    social_security_number_encrypted = Column(Text, nullable=True)
    date_of_birth_encrypted = Column(Text, nullable=False)
    
    # Non-encrypted demographic information
    gender = Column(Enum(Gender), nullable=True)
    marital_status = Column(Enum(MaritalStatus), nullable=True)
    
    # Encrypted contact information
    phone_encrypted = Column(Text, nullable=True)
    email_encrypted = Column(Text, nullable=True)
    emergency_contact_encrypted = Column(Text, nullable=True)
    emergency_phone_encrypted = Column(Text, nullable=True)
    
    # Encrypted address information
    address_line_1_encrypted = Column(Text, nullable=True)
    address_line_2_encrypted = Column(Text, nullable=True)
    city_encrypted = Column(Text, nullable=True)
    state_encrypted = Column(Text, nullable=True)
    zip_code_encrypted = Column(Text, nullable=True)
    country_encrypted = Column(Text, nullable=True)
    
    # Medical information
    preferred_language = Column(String(10), nullable=True)
    race = Column(String(50), nullable=True)
    ethnicity = Column(String(50), nullable=True)
    
    # Status flags
    is_vip = Column(Boolean, default=False)
    is_deceased = Column(Boolean, default=False)
    deceased_date = Column(Date, nullable=True)
    
    # Communication preferences
    preferred_communication = Column(String(20), default="phone")  # phone, email, text, mail
    allow_sms = Column(Boolean, default=True)
    allow_email = Column(Boolean, default=True)
    
    # Financial information
    financial_class = Column(String(20), nullable=True)  # self-pay, insurance, charity, etc.
    credit_score = Column(Integer, nullable=True)
    payment_preference = Column(String(20), nullable=True)  # cash, card, payment_plan
    
    # Relationships
    insurance_policies = relationship("PatientInsurance", back_populates="patient", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="patient")
    bills = relationship("Bill", back_populates="patient")
    documents = relationship("Document", back_populates="patient")
    
    # PHI fields list for redaction
    _phi_fields = [
        'first_name', 'last_name', 'middle_name', 'social_security_number',
        'date_of_birth', 'phone', 'email', 'emergency_contact', 'emergency_phone',
        'address_line_1', 'address_line_2', 'city', 'state', 'zip_code', 'country'
    ]
    
    # Encrypted field descriptors
    first_name = EncryptedField('first_name')
    last_name = EncryptedField('last_name')
    middle_name = EncryptedField('middle_name')
    social_security_number = EncryptedField('social_security_number')
    date_of_birth = EncryptedField('date_of_birth')
    phone = EncryptedField('phone')
    email = EncryptedField('email')
    emergency_contact = EncryptedField('emergency_contact')
    emergency_phone = EncryptedField('emergency_phone')
    address_line_1 = EncryptedField('address_line_1')
    address_line_2 = EncryptedField('address_line_2')
    city = EncryptedField('city')
    state = EncryptedField('state')
    zip_code = EncryptedField('zip_code')
    country = EncryptedField('country')
    
    @hybrid_property
    def full_name(self) -> str:
        """Get patient's full name"""
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(part for part in parts if part)
    
    @hybrid_property
    def age(self) -> Optional[int]:
        """Calculate patient's age"""
        if not self.date_of_birth:
            return None
        
        try:
            dob = datetime.strptime(self.date_of_birth, "%Y-%m-%d").date()
            today = date.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except (ValueError, TypeError):
            return None
    
    @hybrid_property
    def primary_insurance(self) -> Optional['PatientInsurance']:
        """Get primary insurance policy"""
        for insurance in self.insurance_policies:
            if insurance.is_primary and insurance.is_active:
                return insurance
        return None
    
    @hybrid_property
    def secondary_insurance(self) -> Optional['PatientInsurance']:
        """Get secondary insurance policy"""
        for insurance in self.insurance_policies:
            if not insurance.is_primary and insurance.is_active:
                return insurance
        return None
    
    def get_active_insurance_policies(self) -> List['PatientInsurance']:
        """Get all active insurance policies"""
        return [ins for ins in self.insurance_policies if ins.is_active]
    
    def get_formatted_address(self) -> str:
        """Get formatted address string"""
        parts = []
        if self.address_line_1:
            parts.append(self.address_line_1)
        if self.address_line_2:
            parts.append(self.address_line_2)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        
        return ", ".join(parts)
    
    def __repr__(self):
        return f"<Patient(mrn='{self.medical_record_number}', name='{self.full_name}')>"


class InsuranceType(enum.Enum):
    COMMERCIAL = "commercial"
    MEDICARE = "medicare"
    MEDICAID = "medicaid"
    TRICARE = "tricare"
    WORKERS_COMP = "workers_comp"
    AUTO = "auto"
    SELF_PAY = "self_pay"
    OTHER = "other"


class PatientInsurance(BaseModel):
    """Patient insurance information"""
    
    __tablename__ = "patient_insurance"
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Insurance details
    insurance_type = Column(Enum(InsuranceType), nullable=False)
    payer_name = Column(String(100), nullable=False)
    payer_id = Column(String(50), nullable=True)  # National Payer ID
    
    # Encrypted policy information
    policy_number_encrypted = Column(Text, nullable=False)
    group_number_encrypted = Column(Text, nullable=True)
    subscriber_id_encrypted = Column(Text, nullable=True)
    
    # Policy holder information (if different from patient)
    policy_holder_name_encrypted = Column(Text, nullable=True)
    policy_holder_dob_encrypted = Column(Text, nullable=True)
    policy_holder_ssn_encrypted = Column(Text, nullable=True)
    relationship_to_patient = Column(String(20), nullable=True)
    
    # Coverage details
    effective_date = Column(Date, nullable=True)
    termination_date = Column(Date, nullable=True)
    is_primary = Column(Boolean, default=True)
    
    # Coverage amounts
    deductible = Column(Numeric(10, 2), nullable=True)
    out_of_pocket_max = Column(Numeric(10, 2), nullable=True)
    copay = Column(Numeric(10, 2), nullable=True)
    coinsurance_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Verification information
    last_verified_date = Column(Date, nullable=True)
    verification_status = Column(String(20), nullable=True)  # verified, pending, failed
    verification_notes = Column(Text, nullable=True)
    
    # Authorization requirements
    requires_authorization = Column(Boolean, default=False)
    authorization_phone = Column(String(20), nullable=True)
    authorization_website = Column(String(200), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="insurance_policies")
    
    # Encrypted field descriptors
    policy_number = EncryptedField('policy_number')
    group_number = EncryptedField('group_number')
    subscriber_id = EncryptedField('subscriber_id')
    policy_holder_name = EncryptedField('policy_holder_name')
    policy_holder_dob = EncryptedField('policy_holder_dob')
    policy_holder_ssn = EncryptedField('policy_holder_ssn')
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if insurance policy is currently active"""
        today = date.today()
        
        # Check effective date
        if self.effective_date and self.effective_date > today:
            return False
        
        # Check termination date
        if self.termination_date and self.termination_date < today:
            return False
        
        return True
    
    @hybrid_property
    def is_verified(self) -> bool:
        """Check if insurance has been recently verified"""
        if not self.last_verified_date:
            return False
        
        # Consider verified if checked within last 30 days
        days_since_verification = (date.today() - self.last_verified_date).days
        return days_since_verification <= 30
    
    def __repr__(self):
        return f"<PatientInsurance(patient_id={self.patient_id}, payer='{self.payer_name}', primary={self.is_primary})>" 