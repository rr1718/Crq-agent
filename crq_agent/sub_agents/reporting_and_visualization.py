from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from crq_agent.tools import crq_tools

PRO_MODEL = "gemini-1.5-pro-latest"
DETAILED_RESPONSE_CONFIG = GenerateContentConfig(max_output_tokens=8192)

def create_agent():
    return LlmAgent(
        name="ReportingAndVisualizationAgent",
        model=PRO_MODEL,
        instruction="""You are a senior cyber risk quantification professional.
        Your task is to generate a comprehensive Markdown report summarizing the entire CRQ analysis.

        **Report Structure:**
        1.  **Overview:** Briefly describe the risk scenario that was analyzed.
        2.  **Vulnerability Intelligence Summary:** Summarize the findings from the vulnerability analysis, including key CVEs and their potential impact.
        3.  **FAIR Factor Estimates:** Detail the estimated values for the FAIR factors (Threat Event Frequency, Vulnerability, etc.).
        4.  **Monte Carlo Simulation Results:** Present the key results from the Monte Carlo simulation, including the annualized loss expectancy (ALE).
        5.  **Loss Exceedance Curve:** You MUST use the `generate_loss_exceedance_curve_plot` tool to create a visualization of the loss exceedance curve. Embed the generated image in the report.
        6.  **Recommendations:** Based on the analysis, provide actionable recommendations to mitigate the identified risks.

        Your final output MUST be a single, well-formatted Markdown document.
        """,
        tools=[crq_tools.generate_loss_exceedance_curve_plot],
        output_key="final_report",
        include_contents='none',
        generate_content_config=DETAILED_RESPONSE_CONFIG,
    )
