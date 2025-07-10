"""
CrewAI-based agent framework for medical billing agents
"""

import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

from app.utils.logging import get_logger, log_hipaa_event
from app.config import settings


class AgentRole(Enum):
    """Agent role definitions for medical billing"""
    REGISTRATION = "patient_registration"
    CODING = "medical_coding"
    SUBMISSION = "claim_submission"
    FOLLOWUP = "claim_followup"
    BILLING = "patient_billing"
    REPORTING = "financial_reporting"
    RECORDS = "records_integrity"
    COMMUNICATION = "communication"


class MedicalBillingAgent:
    """
    Wrapper class for CrewAI agents in medical billing context
    Provides HIPAA compliance, audit logging, and performance tracking
    """
    
    def __init__(self, agent_id: str, role: AgentRole, crew_agent: Agent):
        self.agent_id = agent_id
        self.role = role
        self.crew_agent = crew_agent
        self.logger = get_logger(f"agent.{role.value}")
        self.task_history = []
        self.performance_metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0
        }
        
        self.logger.info(f"Medical Billing Agent {self.agent_id} ({self.role.value}) initialized")
    
    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task with HIPAA compliance and audit logging"""
        
        task_id = f"task_{datetime.now().isoformat()}_{self.agent_id}"
        start_time = datetime.now()
        
        # Create CrewAI task
        crew_task = Task(
            description=task_description,
            agent=self.crew_agent
        )
        
        # Log task start (HIPAA compliant)
        log_hipaa_event(
            "task_started",
            {
                "agent_id": self.agent_id,
                "task_id": task_id,
                "role": self.role.value,
                "timestamp": start_time.isoformat()
            },
            user_id=context.get("user_id") if context else None,
            patient_id=self._get_patient_id_safe(context) if context else None
        )
        
        try:
            # Execute task using CrewAI
            result = crew_task.execute()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update metrics
            self._update_metrics(execution_time, success=True)
            
            # Log successful completion
            log_hipaa_event(
                "task_completed",
                {
                    "agent_id": self.agent_id,
                    "task_id": task_id,
                    "execution_time": execution_time,
                    "success": True
                },
                user_id=context.get("user_id") if context else None,
                patient_id=self._get_patient_id_safe(context) if context else None
            )
            
            self.logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "execution_time": execution_time,
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update metrics
            self._update_metrics(execution_time, success=False)
            
            # Log failure
            log_hipaa_event(
                "task_failed",
                {
                    "agent_id": self.agent_id,
                    "task_id": task_id,
                    "error": str(e),
                    "execution_time": execution_time
                },
                user_id=context.get("user_id") if context else None,
                patient_id=self._get_patient_id_safe(context) if context else None
            )
            
            self.logger.error(f"Task {task_id} failed: {str(e)}")
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time,
                "agent_id": self.agent_id
            }
    
    def _get_patient_id_safe(self, context: Dict[str, Any]) -> Optional[str]:
        """Safely extract patient ID from context for logging"""
        if not context:
            return None
            
        patient_id = context.get("patient_id")
        if not patient_id:
            patient_info = context.get("patient_info", {})
            patient_id = patient_info.get("patient_id") or patient_info.get("id")
        
        return patient_id
    
    def _update_metrics(self, execution_time: float, success: bool) -> None:
        """Update agent performance metrics"""
        self.performance_metrics["total_tasks"] += 1
        
        if success:
            self.performance_metrics["successful_tasks"] += 1
        else:
            self.performance_metrics["failed_tasks"] += 1
        
        # Update average execution time
        total = self.performance_metrics["total_tasks"]
        current_avg = self.performance_metrics["average_execution_time"]
        new_avg = ((current_avg * (total - 1)) + execution_time) / total
        self.performance_metrics["average_execution_time"] = new_avg
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "performance_metrics": self.performance_metrics,
            "agent_description": self.crew_agent.role
        }


class MedicalBillingCrew:
    """
    CrewAI-based orchestrator for medical billing workflows
    """
    
    def __init__(self):
        self.agents: Dict[str, MedicalBillingAgent] = {}
        self.crews: Dict[str, Crew] = {}
        self.logger = get_logger("billing_crew")
        
        # Initialize LLM for agents
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the language model for agents"""
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            return ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                model_name="gpt-4",
                temperature=0.1
            )
        else:
            # Fallback to a local or mock LLM
            return ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.1
            )
    
    def create_agent(self, agent_id: str, role: AgentRole, goal: str, 
                    backstory: str, tools: List[Any] = None) -> MedicalBillingAgent:
        """Create a new CrewAI agent for medical billing"""
        
        crew_agent = Agent(
            role=role.value.replace("_", " ").title(),
            goal=goal,
            backstory=backstory,
            tools=tools or [],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        medical_agent = MedicalBillingAgent(agent_id, role, crew_agent)
        self.agents[agent_id] = medical_agent
        
        self.logger.info(f"Created agent {agent_id} with role {role.value}")
        return medical_agent
    
    def create_crew(self, crew_name: str, agent_ids: List[str], 
                   process: Process = Process.sequential) -> Crew:
        """Create a crew with specified agents"""
        
        crew_agents = []
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")
            crew_agents.append(self.agents[agent_id].crew_agent)
        
        crew = Crew(
            agents=crew_agents,
            process=process,
            verbose=True
        )
        
        self.crews[crew_name] = crew
        self.logger.info(f"Created crew {crew_name} with agents: {agent_ids}")
        
        return crew
    
    async def execute_crew_task(self, crew_name: str, task_description: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task using a specific crew"""
        
        if crew_name not in self.crews:
            raise ValueError(f"Crew {crew_name} not found")
        
        crew = self.crews[crew_name]
        start_time = datetime.now()
        
        try:
            # Create task for the crew
            task = Task(description=task_description)
            
            # Execute using the crew
            result = crew.kickoff()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Crew {crew_name} completed task in {execution_time:.2f}s")
            
            return {
                "crew_name": crew_name,
                "status": "completed",
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Crew {crew_name} task failed: {str(e)}")
            
            return {
                "crew_name": crew_name,
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def execute_agent_task(self, agent_id: str, task_description: str, 
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task on a specific agent"""
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        return await agent.execute_task(task_description, context)
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        return self.agents[agent_id].get_status()
    
    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents"""
        return {
            agent_id: agent.get_status() 
            for agent_id, agent in self.agents.items()
        }
    
    def list_crews(self) -> List[str]:
        """List all available crews"""
        return list(self.crews.keys())
    
    def list_agents(self) -> Dict[str, str]:
        """List all agents with their roles"""
        return {
            agent_id: agent.role.value 
            for agent_id, agent in self.agents.items()
        }


# ====================================================================
# LEGACY CLASSES FOR BACKWARD COMPATIBILITY
# These classes maintain compatibility with the original agent system
# while the new CrewAI system is being adopted
# ====================================================================

class TaskPriority(Enum):
    """Task priority levels for the agent orchestrator"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class AgentError(Exception):
    """Custom exception for agent operations"""
    def __init__(self, message: str, agent_id: str = None, error_code: str = None):
        super().__init__(message)
        self.agent_id = agent_id
        self.error_code = error_code
        self.timestamp = datetime.now()


class AgentResult:
    """Result wrapper for agent task execution"""
    
    def __init__(self, data: Any = None, success: bool = True, 
                 error: str = None, metadata: Dict[str, Any] = None):
        self.data = data
        self.success = success
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "data": self.data,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class AgentTask:
    """Legacy task representation for compatibility"""
    
    def __init__(self, task_id: str, description: str, 
                 priority: TaskPriority = TaskPriority.NORMAL,
                 context: Dict[str, Any] = None):
        self.task_id = task_id
        self.description = description
        self.priority = priority
        self.context = context or {}
        self.created_at = datetime.now()
        self.status = "pending"
        self.result = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "priority": self.priority.value,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "result": self.result.to_dict() if self.result else None
        }


class BaseAgent:
    """Legacy base agent class for backward compatibility"""
    
    def __init__(self, agent_id: str, name: str = None):
        self.agent_id = agent_id
        self.name = name or agent_id
        self.logger = get_logger(f"legacy_agent.{self.agent_id}")
        self.created_at = datetime.now()
        
        # Bridge to new CrewAI system
        self._crew_agent = None
        self._billing_crew = MedicalBillingCrew()
        
        self.logger.info(f"Legacy agent {self.agent_id} initialized")
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process a task using legacy interface"""
        try:
            # If we have a crew agent, delegate to it
            if self._crew_agent:
                result = await self._crew_agent.execute_task(
                    task.description, 
                    task.context
                )
                
                if result.get("status") == "completed":
                    return AgentResult(
                        data=result.get("result"),
                        success=True,
                        metadata={
                            "task_id": task.task_id,
                            "execution_time": result.get("execution_time"),
                            "agent_id": self.agent_id
                        }
                    )
                else:
                    return AgentResult(
                        success=False,
                        error=result.get("error", "Unknown error"),
                        metadata={
                            "task_id": task.task_id,
                            "agent_id": self.agent_id
                        }
                    )
            else:
                # Fallback to basic processing
                self.logger.warning(f"No CrewAI agent configured for {self.agent_id}")
                return AgentResult(
                    data=f"Legacy processing of: {task.description}",
                    success=True,
                    metadata={"task_id": task.task_id, "agent_id": self.agent_id}
                )
                
        except Exception as e:
            self.logger.error(f"Task processing failed: {str(e)}")
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"task_id": task.task_id, "agent_id": self.agent_id}
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "has_crew_agent": self._crew_agent is not None,
            "type": "legacy_agent"
        }


class AgentOrchestrator:
    """Legacy orchestrator for backward compatibility"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue = []
        self.completed_tasks = []
        self.logger = get_logger("legacy_orchestrator")
        
        # Bridge to new system
        self._crew_system = MedicalBillingCrew()
        
        self.logger.info("Legacy agent orchestrator initialized")
    
    def register_agent(self, agent: BaseAgent):
        """Register a legacy agent"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered legacy agent: {agent.agent_id}")
    
    def create_task(self, description: str, agent_id: str = None,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   context: Dict[str, Any] = None) -> AgentTask:
        """Create a new task"""
        task_id = f"legacy_task_{datetime.now().isoformat()}_{len(self.task_queue)}"
        task = AgentTask(task_id, description, priority, context)
        
        if agent_id:
            task.context["assigned_agent"] = agent_id
        
        self.task_queue.append(task)
        self.logger.info(f"Created task {task_id}")
        return task
    
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a specific task"""
        assigned_agent = task.context.get("assigned_agent")
        
        if assigned_agent and assigned_agent in self.agents:
            agent = self.agents[assigned_agent]
            result = await agent.process_task(task)
        else:
            # Try to find an appropriate agent or use default processing
            result = AgentResult(
                data=f"No suitable agent found for task: {task.description}",
                success=False,
                error="No agent assigned"
            )
        
        task.result = result
        task.status = "completed" if result.success else "failed"
        
        # Move to completed tasks
        if task in self.task_queue:
            self.task_queue.remove(task)
        self.completed_tasks.append(task)
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "registered_agents": len(self.agents),
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "agents": {aid: agent.get_status() for aid, agent in self.agents.items()}
        } 