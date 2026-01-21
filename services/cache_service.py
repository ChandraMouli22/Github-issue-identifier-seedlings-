import os
import json
import hashlib
from pathlib import Path
from typing import Optional

# Cache directory
CACHE_DIR = Path("cache")

def _ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(exist_ok=True)

def _generate_cache_key(repo_url: str, issue_number: int) -> str:
    """
    Generate a unique cache key based on repo URL and issue number.
    Uses hash to create a safe filename.
    """
    raw_key = f"{repo_url}#{issue_number}"
    return hashlib.md5(raw_key.encode()).hexdigest()

def get_cached_analysis(repo_url: str, issue_number: int) -> Optional[dict]:
    """
    Retrieve cached analysis result if it exists.
    
    Args:
        repo_url: GitHub repository URL
        issue_number: Issue number
        
    Returns:
        Cached analysis dict or None if not found
    """
    _ensure_cache_dir()
    
    cache_key = _generate_cache_key(repo_url, issue_number)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                print(f"✓ Cache HIT for {repo_url} #{issue_number}")
                return cached_data
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    print(f"✗ Cache MISS for {repo_url} #{issue_number}")
    return None

def save_to_cache(repo_url: str, issue_number: int, analysis: dict) -> None:
    """
    Save analysis result to cache.
    
    Args:
        repo_url: GitHub repository URL
        issue_number: Issue number
        analysis: Analysis result to cache
    """
    _ensure_cache_dir()
    
    cache_key = _generate_cache_key(repo_url, issue_number)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"✓ Cached analysis for {repo_url} #{issue_number}")
    except Exception as e:
        print(f"Cache write error: {e}")

def clear_cache() -> None:
    """Clear all cached analysis results."""
    _ensure_cache_dir()
    
    for cache_file in CACHE_DIR.glob("*.json"):
        try:
            cache_file.unlink()
        except Exception as e:
            print(f"Error deleting {cache_file}: {e}")
    
    print("✓ Cache cleared")
