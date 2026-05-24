import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from app.orchestrator.hermes_orchestrator import HermesOrchestrator
from app.schemas.report_schema import AgentReport, AgentIssue

# Inform pytest-asyncio that we are testing async functions at the module level
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_repository_data():
    """Fixture to provide sample repository files for testing."""
    return {
        "app/main.py": "import os\ndef start(): print('Platform running')",
        "config.json": "{\"debug\": true}"
    }

@pytest.fixture
def sample_agent_report():
    """Fixture to provide a clean mock structure of a sub-agent report."""
    return AgentReport(
        agent_name="Test Worker Node",
        summary="Everything looks pristine.",
        score=95,
        issues=[
            AgentIssue(
                title="Mock Warning",
                severity="low",
                description="This is a test trace.",
                recommendation="No action required."
            )
        ]
    )


async def test_hermes_orchestrator_successful_flow(mock_repository_data, sample_agent_report):
    """
    Test that HermesOrchestrator correctly triggers sub-agents concurrently,
    aggregates their summaries, calls Ollama Master, and returns the expected schema.
    """
    # 1. Instantiate the orchestrator
    orchestrator = HermesOrchestrator()
    
    # Safeguard the environment configuration attribute during unit tests
    orchestrator.ollama_url = "http://localhost:11434/api/chat"

    # 2. Mock the internal async analyze methods of our sub-agents
    orchestrator.security_agent.analyze = AsyncMock(return_value=sample_agent_report)
    orchestrator.architecture_agent.analyze = AsyncMock(return_value=sample_agent_report)
    orchestrator.planning_agent.analyze = AsyncMock(return_value=sample_agent_report)

    # 3. Mock the external HTTPX call to Ollama Master Manager
    mock_ollama_response = MagicMock()
    mock_ollama_response.status_code = 200
    mock_ollama_response.json.return_value = {
        "message": {
            "content": "{\"overall_summary\": \"Synthesized corporate architectural engineering report complete.\"}"
        }
    }

    # Intercept httpx.AsyncClient.post calls cleanly
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_ollama_response

        # 4. Trigger the orchestration engine execution loop
        result = await orchestrator.run_analysis(
            repo_url="github.com/ApurbaLabs/gotihub-core",
            repository_files=mock_repository_data
        )

        # 5. Assertions: Verify everything executed in alignment with the contract
        assert result["repository"] == "github.com/ApurbaLabs/gotihub-core"
        assert result["overall_summary"] == "Synthesized corporate architectural engineering report complete."
        assert result["code_review_report"] is None
        
        # Verify that our worker nodes were called with the correct parameters
        orchestrator.security_agent.analyze.assert_called_once_with(mock_repository_data)
        orchestrator.architecture_agent.analyze.assert_called_once_with(mock_repository_data)
        
        # Verify the master Ollama payload was dispatched
        mock_post.assert_called_once()


async def test_hermes_orchestrator_ollama_failure_fallback(mock_repository_data, sample_agent_report):
    """
    Test that if the master Ollama server throws an error or times out,
    the orchestrator doesn't crash and returns a safe fallback summary layout.
    """
    orchestrator = HermesOrchestrator()
    
    # Safeguard the environment configuration attribute during unit tests here as well
    orchestrator.ollama_url = "http://localhost:11434/api/chat"

    # Stub out the sub-agents so they return data instantly
    orchestrator.security_agent.analyze = AsyncMock(return_value=sample_agent_report)
    orchestrator.architecture_agent.analyze = AsyncMock(return_value=sample_agent_report)
    orchestrator.planning_agent.analyze = AsyncMock(return_value=sample_agent_report)

    # Simulate an exception trace (like a network timeout) inside the httpx client request
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectTimeout("Ollama worker connection timed out.")):
        
        result = await orchestrator.run_analysis(
            repo_url="github.com/ApurbaLabs/gotihub-core",
            repository_files=mock_repository_data
        )

        # Assertions: Verify the system recovered using its internal try/except boundary fallback
        assert result["repository"] == "github.com/ApurbaLabs/gotihub-core"
        assert "Multi-agent repository evaluation processed" in result["overall_summary"]