from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator, Type
from google.adk.events import Event

PRO_MODEL = "gemini-1.5-pro-latest"

class CRQWorkflowAgent(BaseAgent):
    """
    A custom agent that correctly orchestrates the entire CRQ workflow as a state machine.
    """
    manager: LlmAgent
    risk_scenario_scoper: BaseAgent
    analysis_workflow: SequentialAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        risk_scenario_scoping_module: Type,
        vulnerability_intelligence_module: Type,
        fair_factor_estimation_module: Type,
        quantitative_risk_engine_module: Type,
        reporting_and_visualization_module: Type,
        feedback_module: Type,
    ):
        manager = LlmAgent(
            name="CRQManager",
            model=PRO_MODEL,
            instruction="""You are a helpful manager for a Cyber Risk Quantification process.
            1. Greet the user and ask if they have a risk scenario to quantify.
            2. If they provide a scenario, save it to the session state with the key 'initial_scenario'.
            3. You can also answer general questions about the CRQ process.
            """,
            output_key="initial_scenario"
        )

        risk_scenario_scoper = risk_scenario_scoping_module.create_agent()

        analysis_workflow = SequentialAgent(
            name="AnalysisWorkflow",
            sub_agents=[
                vulnerability_intelligence_module.create_agent(),
                fair_factor_estimation_module.create_agent(),
                quantitative_risk_engine_module.create_agent(),
                reporting_and_visualization_module.create_agent(),
                feedback_module.create_agent(),
            ]
        )

        super().__init__(
            name=name,
            manager=manager,
            risk_scenario_scoper=risk_scenario_scoper,
            analysis_workflow=analysis_workflow,
            sub_agents=[
                manager,
                risk_scenario_scoper,
                analysis_workflow
            ]
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        print(f"[DEBUG CRQWorkflowAgent] --- Start of _run_async_impl ---")
        print(f"[DEBUG CRQWorkflowAgent] Current workflow_step: {ctx.session.state.get("workflow_step", "NOT SET")}")
        print(f"[DEBUG CRQWorkflowAgent] initial_scenario: {ctx.session.state.get("initial_scenario")}")
        print(f"[DEBUG CRQWorkflowAgent] risk_scenario_summary: {ctx.session.state.get("risk_scenario_summary")}")

        if "workflow_step" not in ctx.session.state:
            ctx.session.state["workflow_step"] = "greeting"
            print(f"[DEBUG CRQWorkflowAgent] Initializing workflow_step to greeting.")

        while True:
            current_step = ctx.session.state["workflow_step"]
            print(f"[DEBUG CRQWorkflowAgent] Processing step: {current_step}")

            # Step 1: Greeting. The manager gets the initial scenario.
            if current_step == "greeting":
                print(f"[DEBUG CRQWorkflowAgent] Running manager agent.")
                async for event in self.manager.run_async(ctx):
                    yield event
                
                if ctx.session.state.get("initial_scenario"):
                    ctx.session.state["workflow_step"] = "scoping"
                    print(f"[DEBUG CRQWorkflowAgent] initial_scenario found. Transitioning to scoping.")
                    continue # Continue to the next step in the same turn
                else:
                    print(f"[DEBUG CRQWorkflowAgent] Manager waiting for initial_scenario. Returning.")
                    return # Manager is waiting for input, so we stop and wait for the next turn

            # Step 2: Scoping. The specialist agent refines the scenario.
            elif current_step == "scoping":
                print(f"[DEBUG CRQWorkflowAgent] Running risk_scenario_scoper agent.")
                # Safeguard: If initial_scenario is somehow missing, revert to greeting.
                if not ctx.session.state.get("initial_scenario"):
                    print(f"[DEBUG CRQWorkflowAgent] ERROR: initial_scenario missing in scoping step. Reverting to greeting.")
                    ctx.session.state["workflow_step"] = "greeting"
                    yield Event(type="model_response", author=self.name, content=types.Content(parts=[types.Part(text="Error: Initial scenario missing. Please restart the process by providing a risk scenario.")]))
                    return

                async for event in self.risk_scenario_scoper.run_async(ctx):
                    yield event

                if ctx.session.state.get("risk_scenario_summary"):
                    ctx.session.state["workflow_step"] = "analysis"
                    print(f"[DEBUG CRQWorkflowAgent] risk_scenario_summary found. Transitioning to analysis.")
                    continue # Continue to the next step in the same turn
                else:
                    print(f"[DEBUG CRQWorkflowAgent] Scoper waiting for risk_scenario_summary. Returning.")
                    return # Scoper is waiting for input, so we stop and wait for the next turn

            # Step 3: Analysis. The full sequential workflow runs.
            elif current_step == "analysis":
                print(f"[DEBUG CRQWorkflowAgent] Running analysis_workflow (SequentialAgent).")
                # Safeguard: If risk_scenario_summary is somehow missing, revert to scoping.
                if not ctx.session.state.get("risk_scenario_summary"):
                    print(f"[DEBUG CRQWorkflowAgent] ERROR: risk_scenario_summary missing in analysis step. Reverting to scoping.")
                    ctx.session.state["workflow_step"] = "scoping"
                    yield Event(type="model_response", author=self.name, content=types.Content(parts=[types.Part(text="Error: Risk scenario summary missing. Please provide more details for the risk scenario.")]))
                    return

                async for event in self.analysis_workflow.run_async(ctx):
                    yield event
                
                ctx.session.state["workflow_step"] = "done"
                print(f"[DEBUG CRQWorkflowAgent] Analysis complete. Workflow done.")
                return # Analysis is complete, exit the loop

            # Step 4: Done. The workflow is complete.
            elif current_step == "done":
                print(f"[DEBUG CRQWorkflowAgent] Workflow already done. Returning.")
                return

            # Fallback for unexpected states
            else:
                print(f"[DEBUG CRQWorkflowAgent] ERROR: Unknown workflow step: {current_step}. Resetting workflow.")
                yield Event(type="model_response", author=self.name, content=types.Content(parts=[types.Part(text=f"Error: Unknown workflow step: {current_step}. Resetting workflow.")]))
                ctx.session.state["workflow_step"] = "greeting"
                return