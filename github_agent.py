# /// script
# dependencies = [
#   "acp-sdk>=0.8.1",
#   "PyGithub>=2.1.1",
#   "python-dotenv>=1.0.0",
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

from acp_sdk.models import Message, Metadata
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

# Load environment variables
load_dotenv()

# Create server instance
server = Server()

# Define agent metadata
AGENT_METADATA = {
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

@server.agent(metadata=Metadata(ui={"type": "chat"}))
async def github_agent(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """GitHub integration agent that enables automated GitHub operations."""
    try:
        agent = GitHubAgent()
        
        for message in input:
            try:
                # Parse the command from the message
                command = message.content
                if "list repos" in command.lower():
                    query = command.split("list repos")[-1].strip()
                    repos = agent.list_repositories(query)
                    yield {"thought": "Listing repositories"}
                    yield Message(content=json.dumps(repos, indent=2))
                
                elif "create issue" in command.lower():
                    # Parse issue details from command
                    parts = command.split("create issue")[-1].strip().split(" in ")
                    if len(parts) != 2:
                        yield Message(content="Invalid format. Use: create issue <title> <body> in <repo>")
                        continue
                    
                    issue_details = parts[0].strip().split(" ", 1)
                    if len(issue_details) != 2:
                        yield Message(content="Invalid format. Use: create issue <title> <body> in <repo>")
                        continue
                    
                    title, body = issue_details
                    repo_name = parts[1].strip()
                    
                    result = agent.create_issue(repo_name, title, body)
                    if "error" in result:
                        yield Message(content=result["error"])
                    else:
                        yield {"thought": "Creating issue"}
                        yield Message(content=json.dumps(result, indent=2))
                
                elif "review pr" in command.lower():
                    # Parse PR details from command
                    parts = command.split("review pr")[-1].strip().split(" in ")
                    if len(parts) != 2:
                        yield Message(content="Invalid format. Use: review pr <number> in <repo>")
                        continue
                    
                    pr_number = int(parts[0].strip())
                    repo_name = parts[1].strip()
                    
                    result = agent.review_pull_request(repo_name, pr_number)
                    if "error" in result:
                        yield Message(content=result["error"])
                    else:
                        yield {"thought": "Reviewing pull request"}
                        yield Message(content=json.dumps(result, indent=2))
                
                elif "analyze code" in command.lower():
                    # Parse analysis details from command
                    parts = command.split("analyze code")[-1].strip().split(" in ")
                    if len(parts) != 2:
                        yield Message(content="Invalid format. Use: analyze code <path> in <repo>")
                        continue
                    
                    path = parts[0].strip()
                    repo_name = parts[1].strip()
                    
                    result = agent.analyze_code(repo_name, path)
                    if "error" in result:
                        yield Message(content=result["error"])
                    else:
                        yield {"thought": "Analyzing code"}
                        yield Message(content=json.dumps(result, indent=2))
                
                else:
                    yield Message(content="Unknown command. Available commands:\n" +
                                      "- list repos [query]\n" +
                                      "- create issue <title> <body> in <repo>\n" +
                                      "- review pr <number> in <repo>\n" +
                                      "- analyze code <path> in <repo>")
            
            except Exception as e:
                yield Message(content=f"Error: {str(e)}")
    except Exception as e:
        yield Message(content=f"Fatal Error: {str(e)}")

@server.agent(metadata=Metadata(ui={"type": "health"}))
async def health_check(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Health check endpoint for container orchestration."""
    yield Message(content=json.dumps({"status": "healthy", "metadata": AGENT_METADATA}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="0.0.0.0", port=8000) 