import logging
import json
from typing import Dict, List
from app.core.config import settings
from app.schemas.report_schema import (
    AgentIssue,
    AgentReport,
)

from app.services.llm_service import LLMService

logger = logging.getLogger("hermes.agents.planning")

class PlanningAgent:

    def __init__(self):

        self.llm_service = LLMService()
        self.model_name = settings.WORKER_MODEL
        self.system_prompt = (
            "You are an elite Senior Engineering Manager and Systems Architect Agent. Your objective is to compile "
            "security and architectural findings into a highly structured, actionable technical priority roadmap. "
            "You must return your entire response in strict, valid JSON matching the requested schema layout with zero markdown code blocks or conversational text."
        )

    async def analyze(
        self,
        security_summary: str,
        architecture_summary: str,
    ) -> AgentReport:

        user_prompt = f"""
You are a senior engineering manager.

Based on the following reports:

SECURITY REPORT:
{security_summary}

ARCHITECTURE REPORT:
{architecture_summary}

Generate:
- engineering improvement roadmap
- technical priorities
- recommended next steps

Keep response concise and practical.
You must respond with a JSON object that matches this precise layout:
{{
    "summary": "A concise executive overview of the technical roadmap strategy.",
    "score": 90, // Calculated structural architectural score based on roadmap debt.
    "tasks": [
        {{
            "title": "Clear action title (e.g., Environment Variable Isolation or Microservices Decoupling)",
            "priority_level": "high" or "medium" or "low" or "info",
            "analysis": "Detailed technical explanation of why this step is critical.",
            "execution_step": "Exact engineering implementation instructions."
        }}
    ]
}}
"""
        # Enforcing identical structured payload configuration for consistency across the grid
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json", # Dictates structured response generation from Gemma
            "stream": False
        }
        try:
            # Dispatch payload down to the internal local worker
            ai_raw_response = await self.llm_service.generate_response(payload)
            data = json.loads(ai_raw_response)
            
            issues_list: List[AgentIssue] = []
            
            # Map Gemma's strategic tasks array beautifully into your explicit schema structures
            for task in data.get("tasks", []):
                issues_list.append(
                    AgentIssue(
                        title=task.get("title", "Roadmap Priority Item"),
                        severity=task.get("priority_level", "info").lower(),
                        description=task.get("analysis", "No deep technical analysis provided."),
                        recommendation=task.get("execution_step", "Review general roadmap documentation.")
                    )
                )

            # Fallback if agent skips task generation entirely, ensuring user sees data
            if not issues_list:
                issues_list.append(
                    AgentIssue(
                        title="Master Engineering Roadmap",
                        severity="info",
                        description=data.get("summary", "Roadmap generation complete."),
                        recommendation="Proceed with core platform architectural reviews."
                    )
                )

            return AgentReport(
                agent_name="Gemma Strategic Planning Node",
                summary=data.get("summary", "Engineering roadmap successfully formulated."),
                score=int(data.get("score", 90)),
                issues=issues_list
            )
        except Exception as e:
            logger.error(f"[Hermes Planning Node Failure]: Parsing exception caught. Error: {str(e)}")
            # Fail-safe engine layout so UI interface doesn't hang or drop a 500 error
            return AgentReport(
                agent_name="Gemma Strategic Planning Node",
                summary="Fallback mode triggered: The planning engine encountered a parsing anomaly.",
                score=50,
                issues=[
                    AgentIssue(
                        title="Roadmap Generation Interrupted",
                        severity="medium",
                        description=f"The underlying model output format could not be verified: {str(e)}",
                        recommendation="Verify raw metrics logs and trigger the code scan retry module."
                    )
                ]
            )