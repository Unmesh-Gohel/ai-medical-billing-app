"""
Security middleware for Medical Billing System
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time

from app.utils.logging import get_logger

logger = get_logger("middleware.security")


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for HIPAA compliance and request validation"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.max_request_size = kwargs.get("max_request_size", 10 * 1024 * 1024)  # 10MB
        
    async def dispatch(self, request: Request, call_next):
        """Process security checks for each request"""
        
        start_time = time.time()
        
        # Security headers to add to response
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(f"Request size too large: {content_length}")
            return Response("Request entity too large", status_code=413)
        
        # Check for suspicious patterns
        user_agent = request.headers.get("user-agent", "")
        if self._is_suspicious_user_agent(user_agent):
            logger.warning(f"Suspicious user agent: {user_agent}")
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            return Response("Internal server error", status_code=500)
        
        # Add security headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Add processing time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check for suspicious user agent patterns"""
        suspicious_patterns = [
            "bot", "crawler", "spider", "scraper",
            "wget", "curl", "python-requests"
        ]
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns) 