import pytest
import json
from pathlib import Path
from services.cache_service import (
    _generate_cache_key,
    get_cached_analysis,
    save_to_cache,
    clear_cache
)

# ============================================================================
# Unit Tests for _generate_cache_key
# ============================================================================

@pytest.mark.unit
def test_generate_cache_key_consistency():
    """Test that cache key generation is consistent."""
    key1 = _generate_cache_key("https://github.com/test/repo", 123)
    key2 = _generate_cache_key("https://github.com/test/repo", 123)
    assert key1 == key2

@pytest.mark.unit
def test_generate_cache_key_different_repos():
    """Test that different repos generate different keys."""
    key1 = _generate_cache_key("https://github.com/test/repo1", 1)
    key2 = _generate_cache_key("https://github.com/test/repo2", 1)
    assert key1 != key2

@pytest.mark.unit
def test_generate_cache_key_different_issues():
    """Test that different issue numbers generate different keys."""
    key1 = _generate_cache_key("https://github.com/test/repo", 1)
    key2 = _generate_cache_key("https://github.com/test/repo", 2)
    assert key1 != key2

# ============================================================================
# Unit Tests for get_cached_analysis
# ============================================================================

@pytest.mark.unit
def test_cache_miss(temp_cache_dir):
    """Test cache miss returns None."""
    result = get_cached_analysis("https://github.com/test/repo", 999)
    assert result is None

@pytest.mark.unit
def test_cache_hit(temp_cache_dir):
    """Test cache hit returns cached data."""
    test_data = {
        "summary": "Test summary",
        "type": "bug",
        "priority_score": "3/5",
        "suggested_labels": ["bug"],
        "potential_impact": "Low"
    }
    
    # Save to cache first
    save_to_cache("https://github.com/test/repo", 1, test_data)
    
    # Retrieve from cache
    result = get_cached_analysis("https://github.com/test/repo", 1)
    
    assert result is not None
    assert result["summary"] == "Test summary"
    assert result["type"] == "bug"
    assert result["suggested_labels"] == ["bug"]

@pytest.mark.unit
def test_cache_corrupted_file(temp_cache_dir):
    """Test that corrupted cache file returns None."""
    cache_key = _generate_cache_key("https://github.com/test/repo", 1)
    cache_file = temp_cache_dir / f"{cache_key}.json"
    
    # Write invalid JSON
    cache_file.write_text("invalid json content")
    
    result = get_cached_analysis("https://github.com/test/repo", 1)
    assert result is None

# ============================================================================
# Unit Tests for save_to_cache
# ============================================================================

@pytest.mark.unit
def test_save_to_cache_creates_file(temp_cache_dir):
    """Test that save_to_cache creates a cache file."""
    test_data = {
        "summary": "Test",
        "type": "bug"
    }
    
    save_to_cache("https://github.com/test/repo", 1, test_data)
    
    cache_key = _generate_cache_key("https://github.com/test/repo", 1)
    cache_file = temp_cache_dir / f"{cache_key}.json"
    
    assert cache_file.exists()

@pytest.mark.unit
def test_save_to_cache_valid_json(temp_cache_dir):
    """Test that saved cache contains valid JSON."""
    test_data = {
        "summary": "Test summary",
        "type": "feature_request",
        "priority_score": "4/5",
        "suggested_labels": ["enhancement", "feature"],
        "potential_impact": "High"
    }
    
    save_to_cache("https://github.com/test/repo", 42, test_data)
    
    cache_key = _generate_cache_key("https://github.com/test/repo", 42)
    cache_file = temp_cache_dir / f"{cache_key}.json"
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    assert loaded_data == test_data

@pytest.mark.unit
def test_save_to_cache_overwrites_existing(temp_cache_dir):
    """Test that saving to cache overwrites existing data."""
    old_data = {"summary": "Old"}
    new_data = {"summary": "New"}
    
    save_to_cache("https://github.com/test/repo", 1, old_data)
    save_to_cache("https://github.com/test/repo", 1, new_data)
    
    result = get_cached_analysis("https://github.com/test/repo", 1)
    assert result["summary"] == "New"

# ============================================================================
# Unit Tests for clear_cache
# ============================================================================

@pytest.mark.unit
def test_clear_cache_empty(temp_cache_dir):
    """Test clearing empty cache doesn't raise errors."""
    clear_cache()
    # Should complete without errors

@pytest.mark.unit
def test_clear_cache_removes_files(temp_cache_dir):
    """Test that clear_cache removes all cache files."""
    # Create multiple cache entries
    save_to_cache("https://github.com/test/repo1", 1, {"summary": "Test 1"})
    save_to_cache("https://github.com/test/repo2", 2, {"summary": "Test 2"})
    save_to_cache("https://github.com/test/repo3", 3, {"summary": "Test 3"})
    
    # Verify files exist
    assert len(list(temp_cache_dir.glob("*.json"))) == 3
    
    # Clear cache
    clear_cache()
    
    # Verify all files are removed
    assert len(list(temp_cache_dir.glob("*.json"))) == 0

@pytest.mark.unit
def test_clear_cache_only_json_files(temp_cache_dir):
    """Test that clear_cache only removes JSON files."""
    # Create cache file
    save_to_cache("https://github.com/test/repo", 1, {"summary": "Test"})
    
    # Create non-JSON file
    other_file = temp_cache_dir / "readme.txt"
    other_file.write_text("This should not be deleted")
    
    clear_cache()
    
    # JSON files should be gone
    assert len(list(temp_cache_dir.glob("*.json"))) == 0
    
    # Non-JSON file should remain
    assert other_file.exists()
