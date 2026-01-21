import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from services.github_service import (
    parse_github_url,
    truncate_text,
    get_issue_data
)

# ============================================================================
# Unit Tests for parse_github_url
# ============================================================================

@pytest.mark.unit
def test_parse_github_url_valid():
    """Test parsing valid GitHub URLs."""
    owner, repo = parse_github_url("https://github.com/fastapi/fastapi")
    assert owner == "fastapi"
    assert repo == "fastapi"

@pytest.mark.unit
def test_parse_github_url_with_trailing_slash():
    """Test parsing GitHub URL with trailing slash."""
    owner, repo = parse_github_url("https://github.com/python/cpython/")
    assert owner == "python"
    assert repo == "cpython"

@pytest.mark.unit
def test_parse_github_url_invalid_format():
    """Test parsing invalid GitHub URL raises ValueError."""
    with pytest.raises(ValueError, match="Invalid GitHub URL"):
        parse_github_url("https://github.com/onlyowner")

# ============================================================================
# Unit Tests for truncate_text
# ============================================================================

@pytest.mark.unit
def test_truncate_text_short():
    """Test text shorter than max length is not truncated."""
    text = "Short text"
    result = truncate_text(text, max_length=100)
    assert result == "Short text"

@pytest.mark.unit
def test_truncate_text_long():
    """Test text longer than max length is truncated with ellipsis."""
    text = "a" * 3000
    result = truncate_text(text, max_length=2000)
    assert len(result) == 2003  # 2000 + "..."
    assert result.endswith("...")

@pytest.mark.unit
def test_truncate_text_empty():
    """Test empty string returns empty string."""
    result = truncate_text("")
    assert result == ""

@pytest.mark.unit
def test_truncate_text_none():
    """Test None input returns empty string."""
    result = truncate_text(None)
    assert result == ""

@pytest.mark.unit
def test_truncate_text_exact_length():
    """Test text exactly at max length is not truncated."""
    text = "a" * 2000
    result = truncate_text(text, max_length=2000)
    assert result == text
    assert not result.endswith("...")

# ============================================================================
# Unit Tests for get_issue_data
# ============================================================================

@pytest.mark.unit
async def test_get_issue_data_success():
    """Test successful issue data fetching."""
    mock_issue_response = MagicMock()
    mock_issue_response.status_code = 200
    mock_issue_response.json.return_value = {
        "title": "Test Issue",
        "body": "This is a test issue body"
    }
    
    mock_comments_response = MagicMock()
    mock_comments_response.status_code = 200
    mock_comments_response.json.return_value = [
        {"user": {"login": "user1"}, "body": "First comment"},
        {"user": {"login": "user2"}, "body": "Second comment"}
    ]
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get = AsyncMock(side_effect=[mock_issue_response, mock_comments_response])
        mock_client_class.return_value = mock_client
        
        result = await get_issue_data("https://github.com/test/repo", 1)
        
        assert result["title"] == "Test Issue"
        assert result["body"] == "This is a test issue body"
        assert "user1: First comment" in result["comments"]
        assert "user2: Second comment" in result["comments"]

@pytest.mark.unit
async def test_get_issue_data_not_found():
    """Test 404 error when issue is not found."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ValueError, match="Issue #999 not found"):
            await get_issue_data("https://github.com/test/repo", 999)

@pytest.mark.unit
async def test_get_issue_data_no_comments():
    """Test issue with no comments."""
    mock_issue_response = MagicMock()
    mock_issue_response.status_code = 200
    mock_issue_response.json.return_value = {
        "title": "Test Issue",
        "body": "Test body"
    }
    
    mock_comments_response = MagicMock()
    mock_comments_response.status_code = 200
    mock_comments_response.json.return_value = []
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get = AsyncMock(side_effect=[mock_issue_response, mock_comments_response])
        mock_client_class.return_value = mock_client
        
        result = await get_issue_data("https://github.com/test/repo", 1)
        
        assert result["comments"] == "No comments found."

@pytest.mark.unit
async def test_get_issue_data_no_body():
    """Test issue with no description."""
    mock_issue_response = MagicMock()
    mock_issue_response.status_code = 200
    mock_issue_response.json.return_value = {
        "title": "Test Issue",
        "body": None
    }
    
    mock_comments_response = MagicMock()
    mock_comments_response.status_code = 200
    mock_comments_response.json.return_value = []
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get = AsyncMock(side_effect=[mock_issue_response, mock_comments_response])
        mock_client_class.return_value = mock_client
        
        result = await get_issue_data("https://github.com/test/repo", 1)
        
        assert result["body"] == "No description provided."

@pytest.mark.unit
async def test_get_issue_data_with_github_token(monkeypatch):
    """Test that GitHub token is used when available."""
    monkeypatch.setenv("GITHUB_TOKEN", "test-token-123")
    
    mock_issue_response = MagicMock()
    mock_issue_response.status_code = 200
    mock_issue_response.json.return_value = {
        "title": "Test Issue",
        "body": "Test body"
    }
    
    mock_comments_response = MagicMock()
    mock_comments_response.status_code = 200
    mock_comments_response.json.return_value = []
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get = AsyncMock(side_effect=[mock_issue_response, mock_comments_response])
        mock_client_class.return_value = mock_client
        
        await get_issue_data("https://github.com/test/repo", 1)
        
        # Verify that Authorization header was set
        call_args = mock_client.get.call_args_list[0]
        headers = call_args[1]["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"] == "token test-token-123"
