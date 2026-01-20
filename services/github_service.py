import os
import httpx
from urllib.parse import urlparse

def parse_github_url(url: str):
    """
    Parses a GitHub repository URL to extract owner and repo name.
    """
    try:
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL")
        return path_parts[0], path_parts[1]
    except Exception:
        raise ValueError("Invalid GitHub URL format")

def truncate_text(text: str, max_length: int = 2000) -> str:
    """
    Truncates text to a maximum length.
    """
    if not text:
        return ""
    return text[:max_length] + "..." if len(text) > max_length else text

async def get_issue_data(repo_url: str, issue_number: int):
    """
    Fetches issue details and comments from GitHub using httpx.
    """
    owner, repo = parse_github_url(repo_url)
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Optional: Use GitHub Token if available
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    async with httpx.AsyncClient() as client:
        try:
            # 1. Fetch Issue Details
            issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
            issue_res = await client.get(issue_url, headers=headers)
            
            if issue_res.status_code == 404:
                raise ValueError(f"Issue #{issue_number} not found in {owner}/{repo}")
            issue_res.raise_for_status()
            
            issue_data = issue_res.json()

            # 2. Fetch Comments
            comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
            comments_res = await client.get(comments_url, headers=headers)
            comments_res.raise_for_status()
            
            comments_data = comments_res.json()

            # 3. Process Data
            body = truncate_text(issue_data.get("body") or "No description provided.")
            
            if comments_data:
                comments_summary = "\n".join([
                    f"- {c['user']['login']}: {truncate_text(c['body'], 500)}"
                    for c in comments_data
                ])
            else:
                comments_summary = "No comments found."

            return {
                "title": issue_data.get("title"),
                "body": body,
                "comments": comments_summary
            }

        except httpx.HTTPStatusError as e:
            print(f"GitHub API Error: {e.response.text}")
            raise ValueError(f"GitHub API Error: {e.response.status_code}")
        except Exception as e:
            print(f"Error fetching issue: {str(e)}")
            raise e
