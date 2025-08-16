from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig

PRO_MODEL = "gemini-1.5-pro-latest"
FLASH_MODEL = "gemini-1.5-flash-latest"
DETAILED_RESPONSE_CONFIG = GenerateContentConfig(max_output_tokens=4096)

def create_agent():
    """Creates a resilient agent to gather user feedback on the CRQ report."""
    instruction = """You are a senior cyber risk quantification professional.
    Your task is to present the final report to the user and ask for feedback.

    1.  Present the report from the `final_crq_report` session state variable.
    2.  Ask the user if they are satisfied with the analysis.
    3.  Based on their response, your final output MUST be a single JSON object with one key, `user_feedback`, and one of the following three string values:
        *   `accept`: If the user is happy with the report.
        *   `reject`: If the user wants to stop the analysis.
        *   `revise`: If the user wants to change the FAIR parameters and re-run the simulation.

    Example Output:
    {"user_feedback": "revise"}
    """

    return LlmAgent(
        name="FeedbackAgent",
        model=PRO_MODEL,
        instruction=instruction,
        output_key="user_feedback_decision",
        include_contents='none',
        generate_content_config=DETAILED_RESPONSE_CONFIG,
    )