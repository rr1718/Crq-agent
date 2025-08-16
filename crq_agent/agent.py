from crq_agent.workflow_agent import CRQWorkflowAgent
from crq_agent.sub_agents import (
    risk_scenario_scoping,
    vulnerability_intelligence,
    fair_factor_estimation,
    quantitative_risk_engine,
    reporting_and_visualization,
    feedback,
)

# The root_agent is now the CRQWorkflowAgent itself.
# We pass the modules themselves, not the created agents.
root_agent = CRQWorkflowAgent(
    name="CRQWorkflowAgent",
    risk_scenario_scoping_module=risk_scenario_scoping,
    vulnerability_intelligence_module=vulnerability_intelligence,
    fair_factor_estimation_module=fair_factor_estimation,
    quantitative_risk_engine_module=quantitative_risk_engine,
    reporting_and_visualization_module=reporting_and_visualization,
    feedback_module=feedback,
)