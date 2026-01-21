import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def temp_cache_dir(monkeypatch):
    """Create a temporary cache directory for testing."""
    temp_dir = tempfile.mkdtemp()
    monkeypatch.setattr("services.cache_service.CACHE_DIR", Path(temp_dir))
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("LLM_API_KEY", "test-api-key-12345")
    monkeypatch.setenv("GITHUB_TOKEN", "test-github-token")

@pytest.fixture
def sample_issue_data():
    """Sample issue data for testing."""
    return {
        "title": "Bug: Application crashes on startup",
        "body": "When I try to start the application, it crashes immediately with error code 500.",
        "comments": "- user1: I have the same issue\n- user2: Try clearing your cache"
    }

@pytest.fixture
def sample_analysis_result():
    """Sample LLM analysis result for testing."""
    return {
        "summary": "Application crashes on startup with error code 500",
        "type": "bug",
        "priority_score": "4/5 – Blocks users from using the application",
        "suggested_labels": ["bug", "critical", "needs-investigation"],
        "potential_impact": "Prevents users from accessing the application"
    }

@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for GitHub API calls."""
    mock_client = AsyncMock()
    return mock_client

@pytest.fixture
def mock_genai_model():
    """Mock Google Generative AI model."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"summary": "Test summary", "type": "bug", "priority_score": "3/5", "suggested_labels": ["bug"], "potential_impact": "Low"}'
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    return mock_model
