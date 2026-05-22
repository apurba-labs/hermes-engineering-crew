from typing import Dict

from app.agents.security_agent import SecurityAgent


class HermesOrchestrator:

    def __init__(self):

        self.security_agent = SecurityAgent()

    async def run_analysis(
        self,
        repository_files: Dict[str, str]
    ):

        security_report = await (
            self.security_agent.analyze(repository_files)
        )

        return {
            "security_report": security_report
        }