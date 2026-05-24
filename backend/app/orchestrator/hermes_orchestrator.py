import time
import json
import asyncio
import logging
from typing import Dict, Any
import httpx

from app.core.config import settings
from app.agents.security_agent import SecurityAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.planning_agent import PlanningAgent

logger = logging.getLogger("hermes.orchestrator")

class HermesOrchestrator:

    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_URL}/api/chat"
        # Instantiate the 3 specialized worker nodes
        self.security_agent = SecurityAgent()
        self.architecture_agent = ArchitectureAgent()
        self.planning_agent = PlanningAgent()
        
        self.hermes_system_prompt = (
            "You are the Lead Project Orchestrator and Senior Solution Architect Manager powered by Hermes.\n"
            "Your task is to receive individual audit readouts from your specialized sub-agents, "
            "evaluate their severity metrics, synthesize cross-system risks, and generate an overall summary.\n"
            "You must return your output fitting the FinalEngineeringReport JSON model contract perfectly."
        )

    async def run_analysis(self, repo_url: str, repository_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Gathers analysis from Security and Architecture agents concurrently, passes summaries 
        to Planning, and then executes final Managerial synthesis via the Hermes Master model.
        """
        total_start = time.perf_counter()
        print(f"\n[Orchestrator] Starting Full Pipeline for {repo_url}...")
        # ---------------------------------------------------------
        # STAGE 1: CONCURRENT WORKER EXECUTION (Security & Architecture)
        # ---------------------------------------------------------
        stage1_start = time.perf_counter()
        
        # We create the coroutines WITHOUT awaiting them immediately
        security_task = self.security_agent.analyze(repository_files)
        architecture_task = self.architecture_agent.analyze(repository_files)
        
        # asyncio.gather fires BOTH tasks at the exact same moment across your virtual network highway
        sec_report, arch_report = await asyncio.gather(security_task, architecture_task)
        
        stage1_elapsed = time.perf_counter() - stage1_start
        print(f"[TELEMETRY] Stage 1 (Security + Architecture Agents) took {stage1_elapsed:.2f} seconds.")
    
        # ---------------------------------------------------------
        # STAGE 2: DEPENDENT STRATEGIC PLANNING
        # ---------------------------------------------------------
        stage2_start = time.perf_counter()
        
        # The planning agent requires the resolved summaries from Stage 1
        plan_report = await self.planning_agent.analyze(
            security_summary=sec_report.summary,
            architecture_summary=arch_report.summary
        )
        
        stage2_elapsed = time.perf_counter() - stage2_start
        print(f"[TELEMETRY] Stage 2 (Planning Agent Execution) took {stage2_elapsed:.2f} seconds.")
        
        # ---------------------------------------------------------
        # STAGE 3: MASTER SYNTHESIS AGGREGATION (Hermes Master Manager)
        # ---------------------------------------------------------
        stage3_start = time.perf_counter()
        
        # compiled_crew_insights = {
        #     "security_report_data": {
        #         "summary": sec_report.summary,
        #         "score": sec_report.score,
        #         "issues": [issue.model_dump() for issue in sec_report.issues] 
        #     },
        #     "architecture_report_data": {
        #         "summary": arch_report.summary,
        #         "score": arch_report.score,
        #         "issues": [issue.model_dump() for issue in arch_report.issues]
        #     },
        #     "planning_report_data": {
        #         "summary": plan_report.summary,
        #         "score": plan_report.score,
        #         "tasks": [task.model_dump() for task in plan_report.issues]
        #     }
        # }
        
        hermes_context = f"""
[SECURITY SUMMARY]
Score: {sec_report.score}
{sec_report.summary}

[ARCHITECTURE SUMMARY]
Score: {arch_report.score}
{arch_report.summary}

[PLANNING SUMMARY]
Score: {plan_report.score}
{plan_report.summary}
"""
        
        hermes_payload = {
            "model": settings.MASTER_MODEL, # "gemma-hermes"
            "messages": [
                {"role": "system", "content": self.hermes_system_prompt},
                {
                    "role": "user", 
                    "content": (
                        f"Target Repository: {repo_url}\n\n"
                        f"Here are the raw results injected from the background Gemma agents:\n"
                        f"{hermes_context}\n\n"
                        f"Please synthesize these logs and output your required overall_summary inside a JSON block matching this format:\n"
                        f"{{\n  \"overall_summary\": \"Generate a concise engineering executive summary highlighting the most important technical risks and priorities.\"\n}}"
                    )
                }
            ],
            "format": "json", # Mandates structured JSON output response configuration
            "stream": False
        }
        
        overall_summary = "Multi-agent repository evaluation processed across all active modules successfully."
        
        try:
            # Dispatch the payload bundle down to your Ollama container service
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(self.ollama_url, json=hermes_payload)
                if res.status_code == 200:
                    raw_content = res.json()["message"]["content"]

                    try:
                        start = raw_content.find("{")
                        end = raw_content.rfind("}") + 1
                        cleaned_json = raw_content[start:end]
                        parsed_hermes = json.loads(cleaned_json)
                    except Exception as parse_error:
                        logger.warning(f"[Hermes JSON Cleanup Failure]: {str(parse_error)}")
                        parsed_hermes = {}
                        
                    overall_summary = parsed_hermes.get("overall_summary", overall_summary)
                else:
                    logger.warning(f"[Orchestrator] Master layer returned status code: {res.status_code}")
        except Exception as e:
            logger.error(f"[Orchestrator Error] Hermes master aggregation phase hit an exception: {str(e)}")

        stage3_elapsed = time.perf_counter() - stage3_start
        print(f"[TELEMETRY] Stage 3 (Hermes Master Synthesis API Call) took {stage3_elapsed:.2f} seconds.")
    
        # ---------------------------------------------------------
        # TOTAL PIPELINE METRICS
        # ---------------------------------------------------------
        total_elapsed = time.perf_counter() - total_start
        print(f"[TELEMETRY] Pipeline Complete! Total Runtime: {total_elapsed:.2f} seconds.\n")
        
        # Finally, return the beautifully structured consolidated dictionary back to your API router
        return {
            "repository": repo_url,
            "overall_summary": overall_summary,
            "security_report": {
                "agent_name": sec_report.agent_name,
                "summary": sec_report.summary,
                "score": sec_report.score,
                "issues": sec_report.issues
            },
            "architecture_report": {
                "agent_name": arch_report.agent_name,
                "summary": arch_report.summary,
                "score": arch_report.score,
                "issues": arch_report.issues
            },
            "planning_report": {
                "agent_name": plan_report.agent_name,
                "summary": plan_report.summary,
                "score": plan_report.score,
                "issues": plan_report.issues
            },
            "code_review_report": None # Explicitly maps to your frontend schema hierarchy requirement
        }