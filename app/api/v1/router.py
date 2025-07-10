"""
Main API router for Medical Billing System v1
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

@api_router.get("/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "message": "Medical Billing System API v1",
        "version": "1.0.0",
        "status": "operational"
    }

@api_router.get("/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "healthy",
        "endpoints": [
            "/crewai/agents",
            "/crewai/crews", 
            "/crewai/agents/execute",
            "/crewai/crews/execute"
        ]
    } 