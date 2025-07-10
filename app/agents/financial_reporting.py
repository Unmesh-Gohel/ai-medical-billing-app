"""
Financial Reporting Agent - CrewAI Implementation

This agent specializes in financial reporting, analytics, and performance metrics
with predictive insights and benchmarking capabilities.
"""

from crewai import Agent, Task
from typing import Dict, Any, List

from app.agents.base import MedicalBillingAgent, MedicalBillingCrew
from app.tools import (
    FinancialReportTool,
    PerformanceAnalyticsTool,
    ClaimLookupTool,
    PatientLookupTool,
    TeamCollaborationTool
)
from app.utils.logging import get_logger

logger = get_logger("agents.financial_reporting")


def create_financial_reporting_agent() -> Agent:
    """Create Financial Reporting Agent using CrewAI framework"""
    
    # Initialize tools for financial reporting
    tools = [
        FinancialReportTool(),
        PerformanceAnalyticsTool(),
        ClaimLookupTool(),
        PatientLookupTool(),
        TeamCollaborationTool()
    ]
    
    agent = MedicalBillingAgent(
        role="Financial Reporting Analyst",
        goal=(
            "Generate comprehensive financial reports, analyze revenue cycle performance, "
            "provide predictive insights, and create executive dashboards to support "
            "strategic decision-making and operational optimization."
        ),
        backstory=(
            "You are an expert financial analyst with deep knowledge of healthcare "
            "revenue cycle metrics, financial reporting standards, and business intelligence. "
            "You have extensive experience in data analysis, trend identification, and "
            "predictive modeling. Your expertise includes KPI development, benchmarking "
            "analysis, and executive reporting. You work collaboratively with leadership "
            "teams to translate data into actionable insights and strategic recommendations "
            "for revenue optimization and operational improvement."
        ),
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=3,
        allow_delegation=True
    )
    
    return agent


class FinancialReportingTasks:
    """Pre-defined tasks for Financial Reporting Agent"""
    
    @staticmethod
    def generate_executive_dashboard(reporting_data: Dict[str, Any]) -> Task:
        """Task to generate executive financial dashboard"""
        
        reporting_json = str(reporting_data)
        
        return Task(
            description=f"""
            Generate comprehensive executive financial dashboard for the following period:
            
            {reporting_json}
            
            Dashboard requirements:
            1. Key financial metrics and KPIs with trend analysis
            2. Revenue cycle performance indicators
            3. Payer mix analysis and reimbursement trends
            4. Denial rates and collection performance
            5. Operational efficiency metrics
            6. Comparative analysis against benchmarks
            7. Visual representations and executive summaries
            
            Use FinancialReportTool to generate summary reports.
            Use PerformanceAnalyticsTool for KPI dashboard creation.
            """,
            expected_output=(
                "Executive dashboard with key metrics, visual charts, trend analysis, "
                "performance indicators, and strategic insights formatted as structured "
                "JSON with embedded visualization data."
            ),
            agent=None
        )
    
    @staticmethod
    def analyze_revenue_trends(trend_data: Dict[str, Any]) -> Task:
        """Task to analyze revenue trends and patterns"""
        
        trend_json = str(trend_data)
        
        return Task(
            description=f"""
            Analyze revenue trends and identify patterns from the following data:
            
            {trend_json}
            
            Revenue analysis requirements:
            1. Monthly and quarterly revenue trend analysis
            2. Service line performance and profitability
            3. Provider productivity and efficiency metrics
            4. Seasonal patterns and cyclical trends
            5. Payer performance and contract analysis
            6. Geographic and demographic revenue patterns
            7. Forecasting models and projections
            
            Use FinancialReportTool for detailed revenue analysis.
            Use PerformanceAnalyticsTool for predictive insights.
            """,
            expected_output=(
                "Comprehensive revenue trend analysis with patterns identified, forecasting "
                "models, profitability insights, and strategic recommendations formatted "
                "as structured JSON with trend visualizations."
            ),
            agent=None
        )
    
    @staticmethod
    def create_denial_analytics(denial_data: Dict[str, Any]) -> Task:
        """Task to create denial analytics and reporting"""
        
        denial_json = str(denial_data)
        
        return Task(
            description=f"""
            Create comprehensive denial analytics and reporting from the following data:
            
            {denial_json}
            
            Denial analytics requirements:
            1. Denial rate trends by payer, provider, and service type
            2. Root cause analysis and categorization
            3. Financial impact assessment and recovery potential
            4. Appeal success rates and outcome tracking
            5. Prevention opportunity identification
            6. Benchmarking against industry standards
            7. Predictive modeling for denial risk
            
            Use FinancialReportTool for denial-specific reporting.
            Use PerformanceAnalyticsTool for benchmarking analysis.
            """,
            expected_output=(
                "Detailed denial analytics report with trends, root causes, financial impact, "
                "prevention strategies, and performance benchmarks formatted as structured "
                "JSON with analytical insights."
            ),
            agent=None
        )
    
    @staticmethod
    def generate_collections_analysis(collections_data: Dict[str, Any]) -> Task:
        """Task to generate collections performance analysis"""
        
        collections_json = str(collections_data)
        
        return Task(
            description=f"""
            Generate collections performance analysis from the following data:
            
            {collections_json}
            
            Collections analysis requirements:
            1. Collection rates and aging analysis
            2. Payment method performance and trends
            3. Patient payment behavior analysis
            4. Bad debt trends and write-off analysis
            5. Collections workflow efficiency metrics
            6. Cost-to-collect ratios and ROI analysis
            7. Optimization recommendations and strategies
            
            Use FinancialReportTool for collections reporting.
            Use PerformanceAnalyticsTool for efficiency analysis.
            """,
            expected_output=(
                "Collections performance analysis with rates, trends, efficiency metrics, "
                "optimization opportunities, and strategic recommendations formatted as "
                "structured JSON with performance indicators."
            ),
            agent=None
        )
    
    @staticmethod
    def create_predictive_insights(analytics_data: Dict[str, Any]) -> Task:
        """Task to create predictive insights and forecasting"""
        
        analytics_json = str(analytics_data)
        
        return Task(
            description=f"""
            Create predictive insights and forecasting models from the following data:
            
            {analytics_json}
            
            Predictive analytics requirements:
            1. Revenue forecasting models and projections
            2. Collection probability and cash flow predictions
            3. Denial risk assessment and prevention opportunities
            4. Capacity planning and resource optimization
            5. Market trend analysis and competitive positioning
            6. Scenario modeling and what-if analysis
            7. Strategic planning recommendations
            
            Use PerformanceAnalyticsTool for predictive modeling.
            Use FinancialReportTool for scenario analysis.
            Use TeamCollaborationTool for strategic coordination.
            """,
            expected_output=(
                "Predictive insights report with forecasting models, risk assessments, "
                "optimization opportunities, strategic recommendations, and scenario "
                "analysis formatted as structured JSON with predictive data."
            ),
            agent=None
        )


def create_financial_reporting_crew(reporting_data: Dict[str, Any]) -> MedicalBillingCrew:
    """Create a crew for comprehensive financial reporting workflow"""
    
    # Create the reporting agent
    reporting_agent = create_financial_reporting_agent()
    
    # Create tasks for the reporting workflow
    tasks = [
        FinancialReportingTasks.generate_executive_dashboard(reporting_data),
        FinancialReportingTasks.analyze_revenue_trends(reporting_data.get("revenue_data", {})),
        FinancialReportingTasks.create_denial_analytics(reporting_data.get("denial_data", {})),
        FinancialReportingTasks.create_predictive_insights(reporting_data.get("analytics_data", {}))
    ]
    
    # Assign agent to tasks
    for task in tasks:
        task.agent = reporting_agent
    
    # Create crew
    crew = MedicalBillingCrew(
        agents=[reporting_agent],
        tasks=tasks,
        verbose=True,
        memory=True,
        process="sequential"
    )
    
    return crew


# Example usage function for testing
async def process_financial_reporting(reporting_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process financial reporting workflow"""
    
    try:
        # Create reporting crew
        crew = create_financial_reporting_crew(reporting_data)
        
        # Execute reporting workflow
        result = crew.kickoff()
        
        logger.info(f"Financial reporting completed for period {reporting_data.get('period', 'unknown')}")
        
        return {
            "status": "success",
            "period": reporting_data.get("period"),
            "reporting_result": result,
            "processed_at": reporting_data.get("processed_at")
        }
        
    except Exception as e:
        error_msg = f"Financial reporting failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "period": reporting_data.get("period"),
            "error": error_msg
        } 