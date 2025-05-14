# /// script
# dependencies = [
#   "acp-sdk==0.8.1",
#   "PyGithub>=2.1.1",
#   "python-dotenv>=1.0.0",
#   "langchain>=0.1.0",
# ]
# ///

import asyncio
from collections.abc import AsyncGenerator
from typing import List, Dict, Optional, Any
from github import Github
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest
import os
from dotenv import load_dotenv
import json
import yaml

# Load environment variables
load_dotenv()

class GitHubAgent:
    def __init__(self, github_token: Optional[str] = None):
        """Initialize the GitHub agent with authentication."""
        self.github_token = github_token or os.getenv('GITHUB_AGENT_GITHUB_TOKEN')
        # Initialize GitHub client without token for public access
        self.github = Github()

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for BeeAI integration."""
        return {
            "name": "GitHub Agent",
            "description": "A GitHub integration agent that enables automated GitHub operations",
            "version": "1.0.0",
            "type": "chat",
            "capabilities": [
                "list_repositories",
                "create_issue",
                "review_pull_request",
                "analyze_code"
            ],
            "required_env_vars": ["GITHUB_AGENT_GITHUB_TOKEN"]
        }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming requests from BeeAI."""
        action = request.get("action")
        params = request.get("params", {})

        try:
            if action == "list_repositories":
                result = self.list_repositories(params.get("query", ""))
                return {"status": "success", "data": result}
            
            elif action == "create_issue":
                result = self.create_issue(
                    params.get("repo_name"),
                    params.get("title"),
                    params.get("body"),
                    params.get("labels")
                )
                return {"status": "success", "data": result}
            
            elif action == "review_pull_request":
                result = self.review_pull_request(
                    params.get("repo_name"),
                    params.get("pr_number")
                )
                return {"status": "success", "data": result}
            
            elif action == "analyze_code":
                result = self.analyze_code(
                    params.get("repo_name"),
                    params.get("path", "")
                )
                return {"status": "success", "data": result}
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def list_repositories(self, query: str = "") -> List[Dict[str, Any]]:
        """List repositories with optional search query."""
        try:
            # Search public repositories
            repos = self.github.search_repositories(query=query)
            return [{"name": repo.name, "url": repo.html_url} for repo in repos]
        except Exception as e:
            return [{"error": f"Error listing repositories: {str(e)}"}]

    def create_issue(self, repo_name: str, title: str, body: str, labels: List[str] = None) -> Dict[str, Any]:
        """Create a new issue in a repository."""
        if not self.github_token:
            return {"error": "GitHub token required for creating issues"}
        try:
            repo = self.github.get_user().get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body, labels=labels or [])
            return {
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url
            }
        except Exception as e:
            return {"error": f"Error creating issue: {str(e)}"}

    def review_pull_request(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Review a pull request and provide analysis."""
        try:
            # Get repository by full name (owner/repo)
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            files_changed = pr.get_files()
            changes = []
            for file in files_changed:
                changes.append({
                    "filename": file.filename,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes
                })
            
            comments = [comment.body for comment in pr.get_issue_comments()]
            
            return {
                "title": pr.title,
                "state": pr.state,
                "changes": changes,
                "comments": comments,
                "url": pr.html_url
            }
        except Exception as e:
            return {"error": f"Error reviewing PR: {str(e)}"}

    def analyze_code(self, repo_name: str, path: str = "") -> Dict[str, Any]:
        """Analyze code in a repository."""
        try:
            # Get repository by full name (owner/repo)
            repo = self.github.get_repo(repo_name)
            contents = repo.get_contents(path)
            
            if isinstance(contents, list):
                return {
                    "type": "directory",
                    "items": [item.name for item in contents]
                }
            else:
                return {
                    "type": "file",
                    "name": contents.name,
                    "size": contents.size,
                    "url": contents.download_url
                }
        except Exception as e:
            return {"error": f"Error analyzing code: {str(e)}"}

    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a natural language command."""
        try:
            if "list repos" in command.lower():
                query = command.split("list repos")[-1].strip()
                return {"status": "success", "data": self.list_repositories(query)}
            
            elif "create issue" in command.lower():
                parts = command.split("create issue")[-1].strip().split(" in ")
                if len(parts) != 2:
                    return {"status": "error", "message": "Invalid format. Use: create issue <title> <body> in <repo>"}
                
                issue_details = parts[0].strip().split(" ", 1)
                if len(issue_details) != 2:
                    return {"status": "error", "message": "Invalid format. Use: create issue <title> <body> in <repo>"}
                
                title, body = issue_details
                repo_name = parts[1].strip()
                
                result = self.create_issue(repo_name, title, body)
                if "error" in result:
                    return {"status": "error", "message": result["error"]}
                return {"status": "success", "data": result}
            
            elif "review pr" in command.lower():
                parts = command.split("review pr")[-1].strip().split(" in ")
                if len(parts) != 2:
                    return {"status": "error", "message": "Invalid format. Use: review pr <number> in <repo>"}
                
                pr_number = int(parts[0].strip())
                repo_name = parts[1].strip()
                
                result = self.review_pull_request(repo_name, pr_number)
                if "error" in result:
                    return {"status": "error", "message": result["error"]}
                return {"status": "success", "data": result}
            
            elif "analyze code" in command.lower():
                parts = command.split("analyze code")[-1].strip().split(" in ")
                if len(parts) != 2:
                    return {"status": "error", "message": "Invalid format. Use: analyze code <path> in <repo>"}
                
                path = parts[0].strip()
                repo_name = parts[1].strip()
                
                result = self.analyze_code(repo_name, path)
                if "error" in result:
                    return {"status": "error", "message": result["error"]}
                return {"status": "success", "data": result}
            
            else:
                return {
                    "status": "error",
                    "message": "Unknown command. Available commands:\n" +
                              "- list repos [query]\n" +
                              "- create issue <title> <body> in <repo>\n" +
                              "- review pr <number> in <repo>\n" +
                              "- analyze code <path> in <repo>"
                }
        
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Load agent configuration
    with open("agent.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize agent
    agent = GitHubAgent()
    
    # Print agent info
    print(json.dumps(agent.get_agent_info(), indent=2)) 