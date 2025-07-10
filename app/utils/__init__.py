"""
Utility modules for the AI Medical Billing Application
"""

from .logging import get_logger, setup_logging, SecurityLogger

# Optional imports - these modules may not exist yet
try:
    from .ocr import OCRProcessor
    _ocr_available = True
except ImportError:
    OCRProcessor = None
    _ocr_available = False

try:
    from .validation import DataValidator
    _validation_available = True
except ImportError:
    DataValidator = None
    _validation_available = False

try:
    from .eligibility import EligibilityChecker
    _eligibility_available = True
except ImportError:
    EligibilityChecker = None
    _eligibility_available = False

try:
    from .fhir import FHIRClient
    _fhir_available = True
except ImportError:
    FHIRClient = None
    _fhir_available = False

try:
    from .encryption import EncryptionManager
    _encryption_available = True
except ImportError:
    EncryptionManager = None
    _encryption_available = False

try:
    from .audit import AuditLogger
    _audit_available = True
except ImportError:
    AuditLogger = None
    _audit_available = False

__all__ = [
    "get_logger",
    "setup_logging",
    "SecurityLogger"
]

# Add optional modules if available
if _ocr_available:
    __all__.append("OCRProcessor")
if _validation_available:
    __all__.append("DataValidator")
if _eligibility_available:
    __all__.append("EligibilityChecker")
if _fhir_available:
    __all__.append("FHIRClient")
if _encryption_available:
    __all__.append("EncryptionManager")
if _audit_available:
    __all__.append("AuditLogger") 