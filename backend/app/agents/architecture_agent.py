import json
import logging
from typing import Dict, List
from app.core.config import settings
from app.schemas.report_schema import (
    AgentIssue,
    AgentReport,
)
from app.services.llm_service import LLMService
logger = logging.getLogger("hermes.agents.architecture")

class ArchitectureAgent:
    
    def __init__(self):
        self.llm_service = LLMService()
        self.model_name = settings.WORKER_MODEL
        self.system_prompt = (
            "You are an elite Software Architecture Auditor Agent. Your objective is to analyze a project's repository "
            "structure, code modularity, design patterns, and documentation. You must return your complete response "
            "in strict, valid JSON matching the requested schema layout with zero markdown code blocks or conversational text."
        )

    async def analyze(
        self,
        repository_files: Dict[str, str]
    ) -> AgentReport:

        # Assemble project tree and codebase snippets for structural auditing
        file_paths = list(repository_files.keys())
        combined_structure = ""
        for file_path, content in repository_files.items():
            combined_structure += (
                f"\n--- FILE PATH: {file_path} ---\n"
                f"{content[:250]}\n"
            )
            
        user_prompt = f"""
Analyze the architectural health, project layout, and modular design of this codebase:

[PROJECT FILE MATRIX]
{file_paths}

[SOURCE INSIGHT SNIPPETS]
{combined_structure}

[ORCHESTRATION REQUIREMENT]
Evaluate the project for:
1. Component coupling, modularity, and separation of concerns.
2. Code duplication, structure anti-patterns, or missing framework standards.
3. Presence and clarity of structural project documentation (like a README).

Provide a short, punchy security summary detailing any discoveries.
You must respond with a JSON object that matches this precise layout:
{{
    "summary": "A concise architectural design health overview.",
    "score": 100, // Structural health metric from 0-100.
    "flaws": [
        {{
            "title": "Architectural or structural vulnerability identified",
            "impact": "high" or "medium" or "low",
            "analysis": "Technical explanation of the design degradation or missing component.",
            "remedy": "Exact refactoring steps to fix the layout structure."
        }}
    ]
}}
"""     
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json",
            "stream": False
        }
        try:
            ai_raw_response = await self.llm_service.generate_response(payload)
            data = json.loads(ai_raw_response)
            
            issues_list: List[AgentIssue] = []
            
            for flaw in data.get("flaws", []):
                issues_list.append(
                    AgentIssue(
                        title=flaw.get("title", "Design Structure Warning"),
                        severity=flaw.get("impact", "medium").lower(),
                        description=flaw.get("analysis", "No structural analysis supplied."),
                        recommendation=flaw.get("remedy", "Review design pattern implementations.")
                    )
                )

            # Heuristic Baseline Check: Retaining your original validation as a safe programmatic fallback
            has_readme = any("readme" in path.lower() for path in file_paths)
            if not has_readme and not any("documentation" in issue.title.lower() for issue in issues_list):
                issues_list.append(
                    AgentIssue(
                        title="Missing Documentation Baseline",
                        severity="low",
                        description="A structural README file was not detected in the root file tree repository array.",
                        recommendation="Introduce markdown documentation outlining system deployment variables and dependencies."
                    )
                )

            return AgentReport(
                agent_name="Gemma Architecture Review Node",
                summary=data.get("summary", "System architecture map analyzed successfully."),
                score=int(data.get("score", 100)),
                issues=issues_list
            )

        except Exception as e:
            logger.error(f"[Hermes Architecture Node Failure]: Parsing error caught. Trace: {str(e)}")
            return AgentReport(
                agent_name="Gemma Architecture Review Node",
                summary="Fallback mode triggered: Architecture parsing metrics hit an exception stream.",
                score=60,
                issues=[
                    AgentIssue(
                        title="Structural Scan Anomaly",
                        severity="medium",
                        description=f"The localized model formatting matrix encountered an unhandled parsing anomaly: {str(e)}",
                        recommendation="Verify project root tree parameters and invoke a fresh code scanning workflow cycle."
                    )
                ]
            )