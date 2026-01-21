import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from main import app

client = TestClient(app)

# ============================================================================
# Integration Tests for API Endpoints
# ============================================================================

@pytest.mark.integration
def test_health_endpoint():
    """Test /health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.integration
def test_root_endpoint_serves_html():
    """Test root endpoint serves index.html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@pytest.mark.integration
def test_static_css_file():
    """Test serving CSS file."""
    response = client.get("/styles.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]

@pytest.mark.integration
def test_static_js_file():
    """Test serving JavaScript file."""
    response = client.get("/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"].lower()

@pytest.mark.integration
def test_static_file_not_found():
    """Test 404 for non-existent static file."""
    response = client.get("/nonexistent.css")
    assert response.status_code == 404

# ============================================================================
# Integration Tests for /api/analyze Endpoint
# ============================================================================

@pytest.mark.integration
def test_analyze_endpoint_success():
    """Test successful analysis with mocked services."""
    mock_issue_data = {
        "title": "Test Issue",
        "body": "Test body",
        "comments": "No comments"
    }
    
    mock_analysis = {
        "summary": "Test issue summary",
        "type": "bug",
        "priority_score": "3/5",
        "suggested_labels": ["bug"],
        "potential_impact": "Low"
    }
    
    with patch("main.get_issue_data", new_callable=AsyncMock) as mock_get_issue:
        with patch("main.analyze_issue_with_llm", new_callable=AsyncMock) as mock_analyze:
            with patch("main.get_cached_analysis", return_value=None):
                with patch("main.save_to_cache"):
                    mock_get_issue.return_value = mock_issue_data
                    mock_analyze.return_value = mock_analysis
                    
                    response = client.post(
                        "/api/analyze",
                        json={
                            "repoUrl": "https://github.com/test/repo",
                            "issueNumber": 1
                        }
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["summary"] == "Test issue summary"
                    assert data["type"] == "bug"

@pytest.mark.integration
def test_analyze_endpoint_cache_hit():
    """Test that cached results are returned."""
    cached_analysis = {
        "summary": "Cached summary",
        "type": "feature_request",
        "priority_score": "4/5",
        "suggested_labels": ["enhancement"],
        "potential_impact": "Medium"
    }
    
    with patch("main.get_cached_analysis", return_value=cached_analysis):
        response = client.post(
            "/api/analyze",
            json={
                "repoUrl": "https://github.com/test/repo",
                "issueNumber": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Cached summary"
        assert data["type"] == "feature_request"

@pytest.mark.integration
def test_analyze_endpoint_invalid_url():
    """Test 400 error for invalid GitHub URL."""
    with patch("main.get_issue_data", new_callable=AsyncMock) as mock_get_issue:
        mock_get_issue.side_effect = ValueError("Invalid GitHub URL")
        
        with patch("main.get_cached_analysis", return_value=None):
            response = client.post(
                "/api/analyze",
                json={
                    "repoUrl": "invalid-url",
                    "issueNumber": 1
                }
            )
            
            assert response.status_code == 400
            assert "Invalid GitHub URL" in response.json()["detail"]

@pytest.mark.integration
def test_analyze_endpoint_issue_not_found():
    """Test 404 error when issue is not found."""
    with patch("main.get_issue_data", new_callable=AsyncMock) as mock_get_issue:
        mock_get_issue.side_effect = ValueError("Issue #999 not found in test/repo")
        
        with patch("main.get_cached_analysis", return_value=None):
            response = client.post(
                "/api/analyze",
                json={
                    "repoUrl": "https://github.com/test/repo",
                    "issueNumber": 999
                }
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

@pytest.mark.integration
def test_analyze_endpoint_server_error():
    """Test 500 error for unexpected exceptions."""
    with patch("main.get_issue_data", new_callable=AsyncMock) as mock_get_issue:
        mock_get_issue.side_effect = Exception("Unexpected error")
        
        with patch("main.get_cached_analysis", return_value=None):
            response = client.post(
                "/api/analyze",
                json={
                    "repoUrl": "https://github.com/test/repo",
                    "issueNumber": 1
                }
            )
            
            assert response.status_code == 500

@pytest.mark.integration
def test_analyze_endpoint_missing_repo_url():
    """Test validation error when repoUrl is missing."""
    response = client.post(
        "/api/analyze",
        json={
            "issueNumber": 1
        }
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.integration
def test_analyze_endpoint_missing_issue_number():
    """Test validation error when issueNumber is missing."""
    response = client.post(
        "/api/analyze",
        json={
            "repoUrl": "https://github.com/test/repo"
        }
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.integration
def test_analyze_endpoint_invalid_issue_number():
    """Test validation error for invalid issue number type."""
    response = client.post(
        "/api/analyze",
        json={
            "repoUrl": "https://github.com/test/repo",
            "issueNumber": "not-a-number"
        }
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.integration
def test_analyze_endpoint_saves_to_cache():
    """Test that successful analysis is saved to cache."""
    mock_issue_data = {
        "title": "Test",
        "body": "Test body",
        "comments": "No comments"
    }
    
    mock_analysis = {
        "summary": "Test",
        "type": "bug",
        "priority_score": "3/5",
        "suggested_labels": ["bug"],
        "potential_impact": "Low"
    }
    
    with patch("main.get_issue_data", new_callable=AsyncMock) as mock_get_issue:
        with patch("main.analyze_issue_with_llm", new_callable=AsyncMock) as mock_analyze:
            with patch("main.get_cached_analysis", return_value=None):
                with patch("main.save_to_cache") as mock_save:
                    mock_get_issue.return_value = mock_issue_data
                    mock_analyze.return_value = mock_analysis
                    
                    response = client.post(
                        "/api/analyze",
                        json={
                            "repoUrl": "https://github.com/test/repo",
                            "issueNumber": 1
                        }
                    )
                    
                    assert response.status_code == 200
                    # Verify save_to_cache was called
                    mock_save.assert_called_once_with(
                        "https://github.com/test/repo",
                        1,
                        mock_analysis
                    )
