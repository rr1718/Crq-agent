from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from crq_agent.tools import crq_tools

PRO_MODEL = "gemini-1.5-pro-latest"
DETAILED_RESPONSE_CONFIG = GenerateContentConfig(max_output_tokens=4096)

def create_agent():
    return LlmAgent(
        name="QuantitativeRiskEngineAgent",
        model=PRO_MODEL,
        instruction="""You are a senior cyber risk quantification professional.
        Your task is to run a Monte Carlo simulation to quantify the risk.
        First, inform the user that you are running the simulation.
        Then, take the 'fair_parameters' from the session state.
        Use the `run_fair_monte_carlo` tool to perform a Monte Carlo simulation.
        Your final output should be the raw simulation results (list of floats).
        """,
        tools=[crq_tools.run_fair_monte_carlo],
        output_key="simulation_results",
        include_contents='none',
        generate_content_config=DETAILED_RESPONSE_CONFIG,
    )
