"""
Audit middleware for Medical Billing System - HIPAA Compliance
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
from typing import Optional

from app.utils.logging import get_logger, SecurityLogger

logger = get_logger("middleware.audit")
security_logger = SecurityLogger()


class AuditMiddleware(BaseHTTPMiddleware):
    """Audit middleware for HIPAA compliance and detailed request logging"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.log_bodies = kwargs.get("log_bodies", False)  # Be careful with PHI
        self.sensitive_paths = {
            "/api/v1/patients",
            "/api/v1/claims", 
            "/api/v1/crewai/agents/execute",
            "/api/v1/crewai/crews/execute"
        }
        
    async def dispatch(self, request: Request, call_next):
        """Audit and log all requests for compliance"""
        
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}"
        
        # Extract request details
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        auth_header = request.headers.get("authorization", "")
        user_id = self._extract_user_id(auth_header)
        
        # Log request start
        audit_data = {
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "user_id": user_id,
            "timestamp": time.time(),
            "is_sensitive": self._is_sensitive_path(request.url.path)
        }
        
        # Log request body for non-sensitive endpoints (if enabled)
        if self.log_bodies and not audit_data["is_sensitive"]:
            try:
                body = await request.body()
                if body:
                    audit_data["request_body_size"] = len(body)
                    # Don't log actual body content for security
            except Exception as e:
                logger.warning(f"Could not read request body: {e}")
        
        logger.info("Request started", extra=audit_data)
        
        # Process request
        try:
            response = await call_next(request)
            success = True
            error_message = None
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            success = False
            error_message = str(e)
            # Return a generic error response
            from starlette.responses import JSONResponse
            response = JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log audit event for sensitive operations
        if audit_data["is_sensitive"]:
            security_logger.log_access_event(
                resource=request.url.path,
                action=request.method.lower(),
                user_id=user_id,
                ip_address=client_ip,
                success=success,
                details={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "error": error_message
                }
            )
        
        # Log response details
        response_audit_data = {
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": process_time,
            "success": success,
            "response_size": response.headers.get("content-length", "unknown")
        }
        
        if error_message:
            response_audit_data["error"] = error_message
        
        logger.info("Request completed", extra=response_audit_data)
        
        # Add audit headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Audit-Logged"] = "true"
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address with proxy support"""
        # Check for forwarded headers (load balancers, proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        return request.client.host if request.client else "unknown"
    
    def _extract_user_id(self, auth_header: str) -> Optional[str]:
        """Extract user ID from authorization header"""
        # This is a simplified version - in production you'd decode JWT tokens
        if auth_header and auth_header.startswith("Bearer "):
            # TODO: Implement proper JWT decoding
            return "authenticated_user"
        return "anonymous"
    
    def _is_sensitive_path(self, path: str) -> bool:
        """Check if the path contains sensitive medical information"""
        return any(sensitive in path for sensitive in self.sensitive_paths) 