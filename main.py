import os
import logging
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Load environment variables ---
load_dotenv()

# Check for critical environment variables before proceeding
if not os.getenv("GOOGLE_API_KEY"):
    logger.error("Error: GOOGLE_API_KEY environment variable not set.")
    logger.error("Please create a .env file in the 14-crq-agent directory and add your Google AI API key.")
else:
    # Non-critical environment variables can just have warnings
    if not os.getenv("NVD_API_KEY"):
        logger.warning("Warning: NVD_API_KEY environment variable not set. NVD API calls may be limited or fail.")
        logger.warning("Please obtain an NVD API key from https://nvd.nist.gov/developers and add it to your .env file.")

    from crq_agent.agent import root_agent

    async def main():
        session_service = InMemorySessionService()
        runner = Runner(agent=root_agent, app_name="crq_agent", session_service=session_service)
        session = await session_service.create_session(app_name="crq_agent", user_id="user")
        session_id = session.id

        user_input = "Start the CRQ process for a data breach scenario."
        logger.info(f"User input: {user_input}")

        content = types.Content(role='user', parts=[types.Part(text=user_input)])
        
        async for event in runner.run_async(user_id="user", session_id=session_id, new_message=content):
            if event.is_final_response():
                if event.content:
                    logger.info(f"Final response from agent: {event.content.parts[0].text}")
                else:
                    logger.info("Final response from agent is empty.")

        final_session = await session_service.get_session(app_name="crq_agent", user_id="user", session_id=session_id)
        report_path = final_session.state.get("final_crq_report_path")

        if report_path:
            logger.info(f"Reading report from: {report_path}")
            # This is a placeholder for reading the report file. 
            # In a real application, you would read the file from the given path.
            print(f"Report generated at: {report_path}")
        else:
            logger.error("Could not find 'final_crq_report_path' in the session state.")

    if __name__ == "__main__":
        asyncio.run(main())