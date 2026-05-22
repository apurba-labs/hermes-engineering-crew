from typing import Dict, List

from app.schemas.report_schema import (
    AgentIssue,
    AgentReport,
)

from app.services.llm_service import LLMService


class SecurityAgent:

    def __init__(self):

        self.llm_service = LLMService()

    async def analyze(
        self,
        repository_files: Dict[str, str]
    ) -> AgentReport:

        combined_code = ""

        for file_path, content in repository_files.items():

            combined_code += (
                f"\nFILE: {file_path}\n"
                f"{content[:800]}\n"
            )

        prompt = f"""
Review this repository for:
- hardcoded secrets
- insecure configs
- authentication risks

Repository:

{combined_code}

Provide short security summary.
"""

        ai_response = await (
            self.llm_service.generate_response(prompt)
        )

        issues: List[AgentIssue] = []

        if "secret" in ai_response.lower():

            issues.append(
                AgentIssue(
                    title="Potential Secret Exposure",
                    severity="high",
                    description=(
                        "AI detected possible secret-related risks."
                    ),
                    recommendation=(
                        "Review environment variable handling."
                    ),
                )
            )

        return AgentReport(
            agent_name="Security Analyst Node",
            summary=ai_response[:500],
            score=85,
            issues=issues,
        )