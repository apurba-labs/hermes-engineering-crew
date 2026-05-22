from typing import List, Optional
from pydantic import BaseModel


class AgentIssue(BaseModel):
    title: str
    severity: str
    description: str
    recommendation: str


class AgentReport(BaseModel):
    agent_name: str
    summary: str
    score: Optional[int] = None
    issues: List[AgentIssue]


class FinalEngineeringReport(BaseModel):
    repository: str
    overall_summary: str
    architecture_report: Optional[AgentReport] = None
    security_report: Optional[AgentReport] = None
    code_review_report: Optional[AgentReport] = None
    planning_report: Optional[AgentReport] = None