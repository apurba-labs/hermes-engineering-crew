import json
import logging
from typing import Dict, List
from app.core.config import settings
from app.schemas.report_schema import (
    AgentIssue,
    AgentReport,
)

from app.services.llm_service import LLMService

logger = logging.getLogger("hermes.agents.security")

class SecurityAgent:

    def __init__(self):

        self.llm_service = LLMService()
        self.model_name = settings.WORKER_MODEL
        self.system_prompt = (
            "You are a Senior Security Auditor Node inside an autonomous AI crew layout. "
            "Your job is to analyze repository code text blocks and flag critical vulnerabilities. "
            "You must provide concise, definitive findings without conversational fluff."
        )
        
    async def analyze(
        self,
        repository_files: Dict[str, str]
    ) -> AgentReport:

        combined_code = ""

        for file_path, content in repository_files.items():

            combined_code += (
                f"\nFILE: {file_path}\n"
                f"{content[:250]}\n"
            )

        user_prompt = f"""
Review the following repository file nodes for structural software vulnerabilities.
Specifically audit and locate indicators matching:
1. Hardcoded production credentials or API tokens
2. Insecure or wide-open networking/CORS configs
3. Flawed validation or authentication risk paths

Repository Source Tree Snippets:
{combined_code}

Provide a short, punchy security summary detailing any discoveries.
You must respond with a JSON object that matches this precise layout:
{{
    "summary": "A concise summary of all discovered technical risks.",
    "score": 100, // Subtract structural points per vulnerability found. Base score is 100.
    "issues": [
        {{
            "title": "Title of the security issue",
            "severity": "high" or "medium" or "low",
            "description": "Granular technical analysis of the vulnerability.",
            "recommendation": "Exact remediation steps to patch the flaw."
        }}
    ]
}}
"""

        # Structuring the payload matrix explicitly for Gemma's local runtime interface
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json", # Forces Gemma to speak native structured JSON objects
            "stream": False
        }
        try:
            # Dispatch the payload bundle directly down to the core LLM execution layer
            ai_response = await self.llm_service.generate_response(payload)
            
            # De-serialize the raw token stream into a working python mapping
            data = json.loads(ai_response)
                        
            # Transform individual raw items back into typed Pydantic instances safely
            issues_list: List[AgentIssue] = []
            for issue_dict in data.get("issues", []):
                try:
                    issue = AgentIssue(
                        title=issue_dict.get("title", "No Title"),
                        severity=issue_dict.get("severity", "low"),
                        description=issue_dict.get("description", "No Description"),
                        recommendation=issue_dict.get("recommendation", "No Recommendation")
                    )
                    issues_list.append(issue)
                except Exception as e:
                    logger.warning(f"Failed to parse issue: {issue_dict} with error: {e}")
                    continue
            
            return AgentReport(
                agent_name="Gemma Security Analyst Node",
                summary=data.get("summary", "Scanning operations concluded successfully."),
                score=int(data.get("score", 100)),
                issues=issues_list
            )
        except Exception as e:
            logger.error(f"[Hermes Security Node Failure]: Fallback triggered. Error: {str(e)}")
            # Fallback pattern if JSON structural constraints break during intense processing cycles
            return AgentReport(
                agent_name="Gemma Security Analyst Node",
                summary="Fallback mode triggered: The agent encountered an parsing issue during token generation.",
                score=0,
                issues=[
                    AgentIssue(
                        title="Analysis Structural Failure",
                        severity="high",
                        description=f"Automated processing threw an exception trace: {str(e)}",
                        recommendation="Re-run pipeline tracking module over source repository targets."
                    )
                ]
            )