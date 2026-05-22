from typing import Dict, List

from app.schemas.report_schema import (
    AgentIssue,
    AgentReport,
)

from app.services.llm_service import LLMService


class PlanningAgent:

    def __init__(self):

        self.llm_service = LLMService()

    async def analyze(
        self,
        security_summary: str,
        architecture_summary: str,
    ) -> AgentReport:

        prompt = f"""
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
"""

        ai_response = await (
            self.llm_service.generate_response(prompt)
        )

        issues: List[AgentIssue] = []

        issues.append(
            AgentIssue(
                title="Engineering Roadmap",
                severity="info",
                description=(
                    ai_response[:500]
                ),
                recommendation=(
                    "Review roadmap priorities."
                ),
            )
        )

        return AgentReport(
            agent_name="Planning Agent",
            summary="Engineering roadmap generated.",
            score=90,
            issues=issues,
        )