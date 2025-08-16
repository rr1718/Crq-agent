from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from google.adk.tools import google_search

PRO_MODEL = "gemini-1.5-pro-latest"
DETAILED_RESPONSE_CONFIG = GenerateContentConfig(max_output_tokens=8192)

def create_agent():
    return LlmAgent(
        name="FAIRFactorEstimationAgent",
        model=PRO_MODEL,
        instruction="""You are a senior cyber risk quantification professional.
    Your task is to estimate the parameters for the FAIR model based on the risk scenario and vulnerability data.

    **Output Format:**
    Your final output must be a single JSON object with two keys:
    1.  `justification`: A detailed, multi-sentence explanation of *why* you chose your estimates.
    2.  `parameters`: The structured JSON object containing the FAIR parameters. For each parameter, include a `distribution` key ('triangular').

    Example Output:
    ```json
    {
        "justification": "Based on industry benchmarks, the average cost of a data breach in the financial sector is approximately $5 million. I have therefore set the Primary Loss Magnitude with a most likely value of 5,000,000. The Threat Event Frequency is estimated using a triangular distribution as historical data suggests attacks follow this pattern...",
        "parameters": {
            "TEF": {"min": 1, "most_likely": 2, "max": 3, "distribution": "triangular"},
            "Vuln": {"min": 0.1, "most_likely": 0.3, "max": 0.5, "distribution": "triangular"},
            "LM_Primary": {"min": 1000000, "most_likely": 5000000, "max": 10000000, "distribution": "triangular"},
            "LM_Secondary": {"min": 500000, "most_likely": 1500000, "max": 3000000, "distribution": "triangular"}
        }
    }
    ```
    """
,
        output_key="fair_parameters_with_justification",
        include_contents='none',
        generate_content_config=DETAILED_RESPONSE_CONFIG,
    )