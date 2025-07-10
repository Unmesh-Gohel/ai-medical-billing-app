"""
Base model class with common fields and encryption utilities for HIPAA compliance
"""

from datetime import datetime
from typing import Optional, Any
from sqlalchemy import Column, Integer, DateTime, String, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from cryptography.fernet import Fernet
import json
import uuid

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class BaseModel(Base):
    """Base model with common fields and encryption utilities"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # UUID for external references (non-sequential)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
    
    @classmethod
    def encrypt_phi(cls, data: str) -> str:
        """Encrypt Protected Health Information (PHI)"""
        if not data:
            return data
        
        try:
            cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())
            encrypted_data = cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            # Log error but don't expose sensitive information
            print(f"Encryption error: {type(e).__name__}")
            raise ValueError("Failed to encrypt sensitive data")
    
    @classmethod
    def decrypt_phi(cls, encrypted_data: str) -> str:
        """Decrypt Protected Health Information (PHI)"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())
            decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            # Log error but don't expose sensitive information
            print(f"Decryption error: {type(e).__name__}")
            raise ValueError("Failed to decrypt sensitive data")
    
    def to_dict(self, include_phi: bool = False) -> dict:
        """Convert model to dictionary, optionally including PHI"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        
        # Remove PHI fields if not explicitly requested
        if not include_phi:
            phi_fields = getattr(self, '_phi_fields', [])
            for field in phi_fields:
                if field in result:
                    result[field] = "[REDACTED]"
        
        return result
    
    def update_from_dict(self, data: dict, user_id: Optional[str] = None):
        """Update model from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        if user_id:
            self.updated_by = user_id
    
    def soft_delete(self, user_id: Optional[str] = None):
        """Soft delete the record"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        if user_id:
            self.updated_by = user_id


class AuditMixin:
    """Mixin for models that require audit logging"""
    
    def log_access(self, user_id: str, action: str, details: Optional[dict] = None):
        """Log access to this record"""
        from app.models.audit import AuditLog
        
        audit_log = AuditLog(
            user_id=user_id,
            table_name=self.__tablename__,
            record_id=self.id,
            action=action,
            details=json.dumps(details) if details else None,
            ip_address=getattr(self, '_current_ip', None),
            user_agent=getattr(self, '_current_user_agent', None)
        )
        
        return audit_log
    
    def set_request_context(self, ip_address: str, user_agent: str):
        """Set request context for audit logging"""
        self._current_ip = ip_address
        self._current_user_agent = user_agent


class EncryptedField:
    """Descriptor for encrypted fields"""
    
    def __init__(self, field_name: str):
        self.field_name = field_name
        self.encrypted_field_name = f"{field_name}_encrypted"
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        encrypted_value = getattr(instance, self.encrypted_field_name, None)
        if encrypted_value:
            return BaseModel.decrypt_phi(encrypted_value)
        return None
    
    def __set__(self, instance, value):
        if value is not None:
            encrypted_value = BaseModel.encrypt_phi(str(value))
            setattr(instance, self.encrypted_field_name, encrypted_value)
        else:
            setattr(instance, self.encrypted_field_name, None)


def generate_medical_record_number() -> str:
    """Generate a unique medical record number"""
    import random
    import string
    
    # Format: MRN-YYYYMMDD-XXXX (where XXXX is random)
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"MRN-{date_part}-{random_part}"


def generate_claim_number() -> str:
    """Generate a unique claim number"""
    import random
    import string
    
    # Format: CLM-YYYYMMDD-XXXXXX (where XXXXXX is random)
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    return f"CLM-{date_part}-{random_part}"


def generate_bill_number() -> str:
    """Generate a unique bill number"""
    import random
    import string
    
    # Format: BILL-YYYYMMDD-XXXX (where XXXX is random)
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"BILL-{date_part}-{random_part}" 