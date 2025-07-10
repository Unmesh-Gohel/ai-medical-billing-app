"""
Main FastAPI application for AI Medical Billing System
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import structlog
from typing import Optional

from app.config import settings
from app.utils.logging import setup_logging, get_logger, SecurityLogger

# Setup logging first
setup_logging()
logger = get_logger("main")

# Legacy agents (for backward compatibility)
try:
    from app.agents import (
        AgentOrchestrator,
        AgentTask,
        TaskPriority
    )
    legacy_agents_available = True
except ImportError as e:
    logger.warning(f"Legacy agents not available: {e}")
    AgentOrchestrator = None
    AgentTask = None
    TaskPriority = None
    legacy_agents_available = False

# CrewAI agents (optional - may not be available if dependencies are missing)
try:
    from app.agents.registration import create_patient_registration_agent, create_patient_registration_crew
    from app.agents.medical_coding import create_medical_coding_agent, create_medical_coding_crew
    from app.agents.claim_submission import create_claim_submission_agent, create_claim_submission_crew
    from app.agents.denial_management import create_denial_management_agent, create_denial_management_crew
    from app.agents.patient_billing import create_patient_billing_agent, create_patient_billing_crew
    from app.agents.financial_reporting import create_financial_reporting_agent, create_financial_reporting_crew
    from app.agents.data_integrity import create_data_integrity_agent, create_data_integrity_crew
    from app.agents.communication import create_communication_agent, create_communication_crew
    crewai_agents_available = True
except ImportError as e:
    logger.warning(f"CrewAI agents not available: {e}")
    crewai_agents_available = False
    # Create dummy functions to prevent errors
    def create_patient_registration_agent(): return None
    def create_patient_registration_crew(): return None
    def create_medical_coding_agent(): return None
    def create_medical_coding_crew(): return None
    def create_claim_submission_agent(): return None
    def create_claim_submission_crew(): return None
    def create_denial_management_agent(): return None
    def create_denial_management_crew(): return None
    def create_patient_billing_agent(): return None
    def create_patient_billing_crew(): return None
    def create_financial_reporting_agent(): return None
    def create_financial_reporting_crew(): return None
    def create_data_integrity_agent(): return None
    def create_data_integrity_crew(): return None
    def create_communication_agent(): return None
    def create_communication_crew(): return None

from app.api.v1 import api_router
from app.middleware.security import SecurityMiddleware
from app.middleware.audit import AuditMiddleware

# Initialize security logger
security_logger = SecurityLogger()

# Global agent instances
agent_orchestrator: Optional['AgentOrchestrator'] = None
crewai_agents = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    global agent_orchestrator, crewai_agents
    
    logger.info("Starting AI Medical Billing System")
    
    # Initialize legacy agents for backward compatibility
    if legacy_agents_available and AgentOrchestrator:
        try:
            agent_orchestrator = AgentOrchestrator()
            if hasattr(agent_orchestrator, 'initialize'):
                await agent_orchestrator.initialize()
            logger.info("Legacy agent orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize legacy agents: {e}")
            # Don't raise - allow system to start with CrewAI only
    else:
        logger.info("Legacy agents not available - running CrewAI-only mode")
    
    # Initialize CrewAI agents
    if crewai_agents_available:
        try:
            crewai_agents = {
                "patient_registration": create_patient_registration_agent(),
                "medical_coding": create_medical_coding_agent(),
                "claim_submission": create_claim_submission_agent(),
                "denial_management": create_denial_management_agent(),
                "patient_billing": create_patient_billing_agent(),
                "financial_reporting": create_financial_reporting_agent(),
                "data_integrity": create_data_integrity_agent(),
                "communication": create_communication_agent()
            }
            logger.info("CrewAI agents initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI agents: {e}")
            crewai_agents = {}
    else:
        crewai_agents = {}
        logger.info("CrewAI agents not available - dependencies missing")
    
    yield
    
    # Cleanup
    logger.info("Shutting down AI Medical Billing System")
    if agent_orchestrator and hasattr(agent_orchestrator, 'shutdown'):
        await agent_orchestrator.shutdown()
    logger.info("System shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered medical billing system with 8 specialized agents",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(AuditMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000", "https://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Security
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    # TODO: Implement proper JWT token validation
    # For now, return a mock user
    return {"user_id": "test_user", "role": "admin"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Medical Billing System API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global agent_orchestrator, crewai_agents
    
    health_status = {
        "status": "healthy",
        "timestamp": structlog.get_logger().info("Health check requested"),
        "services": {
            "api": "healthy",
            "legacy_agents": "unknown",
            "crewai_agents": "unknown",
            "database": "unknown"
        }
    }
    
    # Check legacy agent orchestrator
    if agent_orchestrator and hasattr(agent_orchestrator, 'get_health_status'):
        try:
            agent_status = await agent_orchestrator.get_health_status()
            health_status["services"]["legacy_agents"] = "healthy" if agent_status.get("healthy") else "unhealthy"
            health_status["legacy_agent_details"] = agent_status
        except Exception as e:
            health_status["services"]["legacy_agents"] = "unhealthy"
            health_status["legacy_agent_error"] = str(e)
    
    # Check CrewAI agents
    if crewai_agents:
        health_status["services"]["crewai_agents"] = "healthy"
        health_status["crewai_agent_count"] = len(crewai_agents)
        health_status["crewai_agents_list"] = list(crewai_agents.keys())
    
    return health_status


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    global agent_orchestrator, crewai_agents
    
    metrics = {
        "timestamp": structlog.get_logger().info("Metrics requested"),
        "system": {
            "uptime": "unknown",
            "memory_usage": "unknown",
            "cpu_usage": "unknown"
        },
        "legacy_agents": {},
        "crewai_agents": {}
    }
    
    if agent_orchestrator and hasattr(agent_orchestrator, 'get_metrics'):
        try:
            agent_metrics = await agent_orchestrator.get_metrics()
            metrics["legacy_agents"] = agent_metrics
        except Exception as e:
            metrics["legacy_agents"] = {"error": str(e)}
    
    if crewai_agents:
        metrics["crewai_agents"] = {
            "total_agents": len(crewai_agents),
            "available_agents": list(crewai_agents.keys()),
            "agent_details": {
                name: {
                    "role": agent.role,
                    "goal": agent.goal[:100] + "..." if len(agent.goal) > 100 else agent.goal,
                    "tools_count": len(agent.tools),
                    "memory_enabled": agent.memory,
                    "verbose": agent.verbose
                }
                for name, agent in crewai_agents.items()
            }
        }
    
    return metrics


@app.post("/api/v1/agents/execute")
async def execute_agent_task(
    request: Request,
    task_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Execute an agent task"""
    global agent_orchestrator
    
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Agent orchestrator not available")
    
    try:
        # Create task
        task = AgentTask(
            task_id=task_data.get("task_id"),
            agent_type=task_data.get("agent_type"),
            action=task_data.get("action"),
            parameters=task_data.get("parameters", {}),
            priority=TaskPriority(task_data.get("priority", 2)),
            user_id=current_user.get("user_id")
        )
        
        # Log task execution
        security_logger.log_access_event(
            resource="agent_task",
            action="execute",
            user_id=current_user.get("user_id"),
            ip_address=request.client.host,
            success=True,
            details={"agent_type": task.agent_type, "action": task.action}
        )
        
        # Execute task
        result = await agent_orchestrator.execute_task(task)
        
        return {
            "success": True,
            "task_id": task.task_id,
            "result": result.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error executing agent task: {e}")
        
        # Log error
        security_logger.log_access_event(
            resource="agent_task",
            action="execute",
            user_id=current_user.get("user_id"),
            ip_address=request.client.host,
            success=False,
            details={"error": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/agents/status")
async def get_agent_status(current_user: dict = Depends(get_current_user)):
    """Get status of all agents"""
    global agent_orchestrator
    
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Agent orchestrator not available")
    
    try:
        status = await agent_orchestrator.get_agent_status()
        return status
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/crewai/agents/execute")
async def execute_crewai_agent(
    request: Request,
    task_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Execute a CrewAI agent task"""
    global crewai_agents
    
    if not crewai_agents:
        raise HTTPException(status_code=503, detail="CrewAI agents not available")
    
    agent_name = task_data.get("agent_name")
    task_description = task_data.get("task_description")
    task_parameters = task_data.get("parameters", {})
    
    if not agent_name or not task_description:
        raise HTTPException(status_code=400, detail="agent_name and task_description are required")
    
    if agent_name not in crewai_agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    try:
        # Log task execution
        security_logger.log_access_event(
            resource="crewai_agent",
            action="execute",
            user_id=current_user.get("user_id"),
            ip_address=request.client.host,
            success=True,
            details={"agent_name": agent_name, "task": task_description}
        )
        
        # Get the agent
        agent = crewai_agents[agent_name]
        
        # Create and execute task
        from crewai import Task
        task = Task(
            description=task_description,
            agent=agent,
            expected_output="Structured JSON response with task completion details"
        )
        
        # Execute the task
        result = task.execute()
        
        return {
            "success": True,
            "agent_name": agent_name,
            "task_description": task_description,
            "result": result,
            "execution_time": "N/A",  # TODO: Add timing
            "user_id": current_user.get("user_id")
        }
        
    except Exception as e:
        logger.error(f"Error executing CrewAI agent task: {e}")
        
        # Log error
        security_logger.log_access_event(
            resource="crewai_agent",
            action="execute",
            user_id=current_user.get("user_id"),
            ip_address=request.client.host,
            success=False,
            details={"error": str(e), "agent_name": agent_name}
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/crewai/crews/execute")
async def execute_crewai_crew(
    request: Request,
    crew_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Execute a CrewAI crew workflow"""
    
    crew_type = crew_data.get("crew_type")
    workflow_data = crew_data.get("workflow_data", {})
    
    if not crew_type:
        raise HTTPException(status_code=400, detail="crew_type is required")
    
    try:
        # Log crew execution
        security_logger.log_access_event(
            resource="crewai_crew",
            action="execute",
            user_id=current_user.get("user_id"),
            ip_address=request.client.host,
            success=True,
            details={"crew_type": crew_type}
        )
        
        # Create and execute crew based on type
        crew = None
        if crew_type == "patient_registration":
            crew = create_patient_registration_crew(workflow_data)
        elif crew_type == "medical_coding":
            crew = create_medical_coding_crew(workflow_data)
        elif crew_type == "claim_submission":
            crew = create_claim_submission_crew(workflow_data)
        elif crew_type == "denial_management":
            crew = create_denial_management_crew(workflow_data)
        elif crew_type == "patient_billing":
            crew = create_patient_billing_crew(workflow_data)
        elif crew_type == "financial_reporting":
            crew = create_financial_reporting_crew(workflow_data)
        elif crew_type == "data_integrity":
            crew = create_data_integrity_crew(workflow_data)
        elif crew_type == "communication":
            crew = create_communication_crew(workflow_data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown crew type: {crew_type}")
        
        # Execute the crew
        result = crew.kickoff()
        
        return {
            "success": True,
            "crew_type": crew_type,
            "result": result,
            "execution_time": "N/A",  # TODO: Add timing
            "user_id": current_user.get("user_id"),
            "agents_involved": len(crew.agents),
            "tasks_completed": len(crew.tasks)
        }
        
    except Exception as e:
        logger.error(f"Error executing CrewAI crew: {e}")
        
        # Log error
        security_logger.log_access_event(
            resource="crewai_crew",
            action="execute",
            user_id=current_user.get("user_id"),
            ip_address=request.client.host,
            success=False,
            details={"error": str(e), "crew_type": crew_type}
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/crewai/agents")
async def list_crewai_agents(current_user: dict = Depends(get_current_user)):
    """List all available CrewAI agents"""
    global crewai_agents
    
    if not crewai_agents:
        return {"agents": [], "count": 0}
    
    agent_list = []
    for name, agent in crewai_agents.items():
        agent_list.append({
            "name": name,
            "role": agent.role,
            "goal": agent.goal,
            "tools_count": len(agent.tools),
            "memory_enabled": agent.memory,
            "verbose": agent.verbose,
            "allow_delegation": agent.allow_delegation
        })
    
    return {
        "agents": agent_list,
        "count": len(agent_list)
    }


@app.get("/api/v1/crewai/crews")
async def list_available_crews(current_user: dict = Depends(get_current_user)):
    """List all available CrewAI crew types"""
    
    crew_types = [
        {
            "name": "patient_registration",
            "description": "Patient intake, registration, and eligibility verification",
            "agents": ["Patient Registration Specialist"],
            "use_cases": ["New patient onboarding", "Insurance verification", "Demographics update"]
        },
        {
            "name": "medical_coding",
            "description": "Medical coding with ICD-10, CPT, and HCPCS",
            "agents": ["Medical Coding Specialist"],
            "use_cases": ["Encounter coding", "Code validation", "Documentation improvement"]
        },
        {
            "name": "claim_submission",
            "description": "Electronic claim generation and submission",
            "agents": ["Claim Submission Specialist"],
            "use_cases": ["Clean claim generation", "Electronic submission", "Status tracking"]
        },
        {
            "name": "denial_management",
            "description": "Denial analysis and appeal generation",
            "agents": ["Denial Management Specialist"],
            "use_cases": ["Denial monitoring", "Appeal generation", "Pattern analysis"]
        },
        {
            "name": "patient_billing",
            "description": "Patient billing and collections management",
            "agents": ["Patient Billing Specialist"],
            "use_cases": ["Statement generation", "Payment processing", "Collections"]
        },
        {
            "name": "financial_reporting",
            "description": "Financial analytics and reporting",
            "agents": ["Financial Reporting Analyst"],
            "use_cases": ["Revenue analysis", "KPI dashboards", "Predictive insights"]
        },
        {
            "name": "data_integrity",
            "description": "Data quality and EHR synchronization",
            "agents": ["Data Integrity Specialist"],
            "use_cases": ["Data validation", "EHR sync", "Duplicate resolution"]
        },
        {
            "name": "communication",
            "description": "Patient communications and team collaboration",
            "agents": ["Communication Specialist"],
            "use_cases": ["Patient messaging", "Team coordination", "Inquiry handling"]
        }
    ]
    
    return {
        "crew_types": crew_types,
        "count": len(crew_types)
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Log security event
    security_logger.log_access_event(
        resource="api",
        action="error",
        ip_address=request.client.host,
        success=False,
        details={"error": str(exc), "path": request.url.path}
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = structlog.get_logger().info("Request started")
    
    # Log request
    logger.info(
        "HTTP Request",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    
    response = await call_next(request)
    
    # Log response
    logger.info(
        "HTTP Response",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        client_ip=request.client.host
    )
    
    return response


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None  # Use our custom logging
    ) 