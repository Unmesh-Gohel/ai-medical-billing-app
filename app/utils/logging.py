"""
Logging utilities with HIPAA compliance and structured logging
"""

import logging
import logging.handlers
import structlog
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from app.config import settings


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove PHI from log data"""
    
    # Fields that should be redacted
    phi_fields = {
        'ssn', 'social_security_number', 'social_security',
        'phone', 'phone_number', 'telephone',
        'email', 'email_address',
        'address', 'address_line_1', 'address_line_2',
        'city', 'state', 'zip_code', 'zipcode',
        'first_name', 'last_name', 'middle_name',
        'date_of_birth', 'dob', 'birth_date',
        'medical_record_number', 'mrn',
        'patient_id', 'member_id', 'subscriber_id',
        'policy_number', 'group_number'
    }
    
    sanitized = {}
    
    for key, value in data.items():
        if key.lower() in phi_fields:
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_log_data(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized


def add_audit_info(logger, method_name, event_dict):
    """Add audit information to log entries"""
    event_dict['audit_timestamp'] = datetime.utcnow().isoformat()
    event_dict['application'] = settings.APP_NAME
    event_dict['version'] = settings.APP_VERSION
    
    # Add user context if available
    if hasattr(event_dict.get('context', {}), 'user_id'):
        event_dict['user_id'] = event_dict['context'].user_id
    
    return event_dict


def setup_logging():
    """Setup structured logging with HIPAA compliance"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            add_audit_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    )
    
    # Setup file handlers
    root_logger = logging.getLogger()
    
    # Application log file
    app_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(app_handler)
    
    # Error log file
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(error_handler)
    
    # Audit log file (for HIPAA compliance)
    audit_handler = logging.handlers.RotatingFileHandler(
        log_dir / "audit.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=50,  # Keep more audit logs
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Create audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    
    # Agent execution log
    agent_handler = logging.handlers.RotatingFileHandler(
        log_dir / "agents.log",
        maxBytes=25 * 1024 * 1024,  # 25MB
        backupCount=10,
        encoding='utf-8'
    )
    agent_handler.setLevel(logging.INFO)
    agent_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Create agent logger
    agent_logger = logging.getLogger('agent')
    agent_logger.addHandler(agent_handler)
    agent_logger.setLevel(logging.INFO)


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> structlog.BoundLogger:
    """Get a structured logger with optional context"""
    logger = structlog.get_logger(name)
    
    if context:
        # Sanitize context to remove PHI
        sanitized_context = sanitize_log_data(context)
        logger = logger.bind(**sanitized_context)
    
    return logger


class HIPAACompliantLogger:
    """HIPAA-compliant logger that automatically sanitizes PHI"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.name = name
    
    def info(self, message: str, **kwargs):
        """Log info message with PHI sanitization"""
        sanitized_kwargs = sanitize_log_data(kwargs)
        self.logger.info(message, **sanitized_kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with PHI sanitization"""
        sanitized_kwargs = sanitize_log_data(kwargs)
        self.logger.warning(message, **sanitized_kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with PHI sanitization"""
        sanitized_kwargs = sanitize_log_data(kwargs)
        self.logger.error(message, **sanitized_kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with PHI sanitization"""
        sanitized_kwargs = sanitize_log_data(kwargs)
        self.logger.debug(message, **sanitized_kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with PHI sanitization"""
        sanitized_kwargs = sanitize_log_data(kwargs)
        self.logger.critical(message, **sanitized_kwargs)
    
    def audit(self, event_type: str, details: Dict[str, Any], user_id: str = None, 
             ip_address: str = None, user_agent: str = None):
        """Log audit event for HIPAA compliance"""
        audit_data = {
            'event_type': event_type,
            'details': sanitize_log_data(details),
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat(),
            'logger_name': self.name
        }
        
        # Use the audit logger
        audit_logger = logging.getLogger('audit')
        audit_logger.info(f"AUDIT: {event_type}", extra=audit_data)
        
        # Also log to the regular logger for debugging
        self.logger.info(f"AUDIT: {event_type}", **audit_data)


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self, name: str):
        self.logger = get_logger(f"performance.{name}")
    
    def log_execution_time(self, operation: str, execution_time: float, 
                          details: Optional[Dict[str, Any]] = None):
        """Log execution time for operations"""
        log_data = {
            'operation': operation,
            'execution_time': execution_time,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            log_data.update(sanitize_log_data(details))
        
        self.logger.info(f"Performance: {operation}", **log_data)
    
    def log_agent_metrics(self, agent_type: str, metrics: Dict[str, Any]):
        """Log agent performance metrics"""
        sanitized_metrics = sanitize_log_data(metrics)
        
        self.logger.info(f"Agent Metrics: {agent_type}", 
                        agent_type=agent_type, 
                        metrics=sanitized_metrics,
                        timestamp=datetime.utcnow().isoformat())


class SecurityLogger:
    """Logger for security events"""
    
    def __init__(self):
        self.logger = get_logger("security")
    
    def log_authentication_event(self, event_type: str, user_id: str = None, 
                                ip_address: str = None, user_agent: str = None,
                                success: bool = True, details: Dict[str, Any] = None):
        """Log authentication events"""
        log_data = {
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            log_data.update(sanitize_log_data(details))
        
        level = "info" if success else "warning"
        getattr(self.logger, level)(f"Security: {event_type}", **log_data)
    
    def log_access_event(self, resource: str, action: str, user_id: str = None,
                        ip_address: str = None, success: bool = True,
                        details: Dict[str, Any] = None):
        """Log resource access events"""
        log_data = {
            'resource': resource,
            'action': action,
            'user_id': user_id,
            'ip_address': ip_address,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            log_data.update(sanitize_log_data(details))
        
        level = "info" if success else "warning"
        getattr(self.logger, level)(f"Access: {action} on {resource}", **log_data) 