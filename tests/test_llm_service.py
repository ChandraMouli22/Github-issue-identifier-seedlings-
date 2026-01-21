import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from services.llm_service import clean_json, analyze_issue_with_llm

# ============================================================================
# Unit Tests for clean_json
# ============================================================================

@pytest.mark.unit
def test_clean_json_with_markdown():
    """Test removing markdown code blocks from JSON."""
    text = '```json\n{"summary": "Test", "type": "bug"}\n```'
    result = clean_json(text)
    assert result == '{"summary": "Test", "type": "bug"}'

@pytest.mark.unit
def test_clean_json_plain():
    """Test plain JSON input is unchanged."""
    text = '{"summary": "Test", "type": "bug"}'
    result = clean_json(text)
    assert result == '{"summary": "Test", "type": "bug"}'

@pytest.mark.unit
def test_clean_json_with_extra_text():
    """Test extracting JSON from text with extra content."""
    text = 'Here is the result:\n{"summary": "Test", "type": "bug"}\nEnd of result'
    result = clean_json(text)
    assert result == '{"summary": "Test", "type": "bug"}'

@pytest.mark.unit
def test_clean_json_multiple_braces():
    """Test extracting JSON with nested objects."""
    text = 'Some text {"outer": {"inner": "value"}} more text'
    result = clean_json(text)
    assert result == '{"outer": {"inner": "value"}}'

@pytest.mark.unit
def test_clean_json_no_braces():
    """Test text without braces returns as-is."""
    text = 'No JSON here'
    result = clean_json(text)
    assert result == 'No JSON here'

# ============================================================================
# Unit Tests for analyze_issue_with_llm
# ============================================================================

@pytest.mark.unit
async def test_analyze_issue_with_llm_success(mock_env_vars, sample_issue_data):
    """Test successful LLM analysis."""
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "summary": "Application crashes on startup",
        "type": "bug",
        "priority_score": "4/5 – Critical issue",
        "suggested_labels": ["bug", "critical"],
        "potential_impact": "High"
    })
    
    with patch("services.llm_service.genai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model
        
        result = await analyze_issue_with_llm(sample_issue_data)
        
        assert result["summary"] == "Application crashes on startup"
        assert result["type"] == "bug"
        assert result["priority_score"] == "4/5 – Critical issue"
        assert "bug" in result["suggested_labels"]

@pytest.mark.unit
async def test_analyze_issue_with_llm_missing_api_key(monkeypatch, sample_issue_data):
    """Test error when LLM_API_KEY is missing."""
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    
    with pytest.raises(ValueError, match="LLM_API_KEY is missing"):
        await analyze_issue_with_llm(sample_issue_data)

@pytest.mark.unit
async def test_analyze_issue_with_llm_invalid_json(mock_env_vars, sample_issue_data):
    """Test error when LLM returns invalid JSON."""
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON"
    
    with patch("services.llm_service.genai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model
        
        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            await analyze_issue_with_llm(sample_issue_data)

@pytest.mark.unit
async def test_analyze_issue_with_llm_retry_on_rate_limit(mock_env_vars, sample_issue_data):
    """Test retry logic on rate limit error."""
    # First two calls fail with rate limit, third succeeds
    rate_limit_error = Exception("429 Resource exhausted")
    
    success_response = MagicMock()
    success_response.text = json.dumps({
        "summary": "Test",
        "type": "bug",
        "priority_score": "3/5",
        "suggested_labels": ["bug"],
        "potential_impact": "Low"
    })
    
    with patch("services.llm_service.genai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(
            side_effect=[rate_limit_error, rate_limit_error, success_response]
        )
        mock_model_class.return_value = mock_model
        
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await analyze_issue_with_llm(sample_issue_data)
            
            # Should have retried twice (slept twice)
            assert mock_sleep.call_count == 2
            # First sleep: 5s, second sleep: 10s
            assert mock_sleep.call_args_list[0][0][0] == 5
            assert mock_sleep.call_args_list[1][0][0] == 10
            
            assert result["summary"] == "Test"

@pytest.mark.unit
async def test_analyze_issue_with_llm_max_retries_exceeded(mock_env_vars, sample_issue_data):
    """Test that max retries are respected."""
    rate_limit_error = Exception("429 quota exceeded")
    
    with patch("services.llm_service.genai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(side_effect=rate_limit_error)
        mock_model_class.return_value = mock_model
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(ValueError, match="AI rate limit reached after 3 retries"):
                await analyze_issue_with_llm(sample_issue_data)

@pytest.mark.unit
async def test_analyze_issue_with_llm_non_rate_limit_error(mock_env_vars, sample_issue_data):
    """Test that non-rate-limit errors are raised immediately."""
    other_error = Exception("Some other error")
    
    with patch("services.llm_service.genai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(side_effect=other_error)
        mock_model_class.return_value = mock_model
        
        with pytest.raises(ValueError, match="Gemini Error"):
            await analyze_issue_with_llm(sample_issue_data)

@pytest.mark.unit
async def test_analyze_issue_with_llm_cleans_markdown_response(mock_env_vars, sample_issue_data):
    """Test that markdown code blocks are cleaned from response."""
    mock_response = MagicMock()
    mock_response.text = '```json\n{"summary": "Test", "type": "bug", "priority_score": "3/5", "suggested_labels": ["bug"], "potential_impact": "Low"}\n```'
    
    with patch("services.llm_service.genai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model
        
        result = await analyze_issue_with_llm(sample_issue_data)
        
        assert result["summary"] == "Test"
        assert result["type"] == "bug"
