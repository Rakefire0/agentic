# /// script
# dependencies = [
#   "acp-sdk>=0.8.1",
#   "PyGithub>=2.1.1",
#   "python-dotenv>=1.0.0",
# ]
# ///

import asyncio
import json
import os
from collections.abc import AsyncGenerator
from typing import List, Dict, Optional, Any

from github import Github
from dotenv import load_dotenv

# Import ACP SDK components
from acp_sdk.models import Message, MessagePart, Metadata
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

# Load environment variables
load_dotenv()

# Create server instance
server = Server()

class GitHubAgent:
    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub agent with authentication."""
        self.token = token or os.getenv('GITHUB_AGENT_GITHUB_TOKEN')
        self.github = None
        if self.token:
            self.github = Github(self.token)
        else:
            self.github = Github()  # Anonymous access for public repos

    def list_repositories(self, query: str = "") -> List[Dict[str, Any]]:
        """List repositories with optional search query."""
        try:
            if not query:
                query = "stars:>100"  # Default: popular repos
            repos = self.github.search_repositories(query=query)
            return [{"name": repo.name, "url": repo.html_url, "stars": repo.stargazers_count} 
                   for repo in repos[:10]]  # Limit to 10 results
        except Exception as e:
            return [{"error": f"Error listing repositories: {str(e)}"}]

    def create_issue(self, repo_name: str, title: str, body: str) -> Dict[str, Any]:
        """Create a new issue in a repository."""
        if not self.token:
            return {"error": "GitHub token required for creating issues"}
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body)
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
            
            return {
                "title": pr.title,
                "state": pr.state,
                "changes": changes,
                "url": pr.html_url
            }
        except Exception as e:
            return {"error": f"Error reviewing PR: {str(e)}"}

    def analyze_code(self, repo_name: str, path: str = "") -> Dict[str, Any]:
        """Analyze code in a repository."""
        try:
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

# Define a helper function to create a text response
def create_text_response(content: str) -> Message:
    """Create a text message response."""
    return Message(parts=[MessagePart(content=content, content_type="text/plain")])

@server.agent(metadata=Metadata(name="github", description="GitHub operations agent", ui={"type": "chat"}))
async def github_agent(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, None]:
    """GitHub integration agent that enables automated GitHub operations."""
    
    # Create a GitHub agent instance
    agent = GitHubAgent()
    
    # Process each message
    for message in input:
        command = message.content.lower() if hasattr(message, 'content') else ""
        
        # Initial thought
        yield RunYield(thought="Processing GitHub command...")
        
        try:
            # Handle different commands
            if "list repos" in command or "show repositories" in command:
                query = command.split("repos")[-1].strip() if "list repos" in command else ""
                result = agent.list_repositories(query)
                response_text = f"Here are the repositories I found:\n\n{json.dumps(result, indent=2)}"
                yield RunYield(message=create_text_response(response_text))
                
            elif "create issue" in command:
                parts = command.split("in repo")
                if len(parts) != 2:
                    yield RunYield(message=create_text_response("Please specify the repository name with 'in repo [name]'"))
                    continue
                    
                issue_details = parts[0].replace("create issue", "").strip()
                repo_name = parts[1].strip()
                
                if " with body " in issue_details:
                    title_body = issue_details.split(" with body ")
                    if len(title_body) == 2:
                        title, body = title_body
                        result = agent.create_issue(repo_name, title, body)
                        response_text = f"Issue creation result:\n\n{json.dumps(result, indent=2)}"
                        yield RunYield(message=create_text_response(response_text))
                    else:
                        yield RunYield(message=create_text_response("Please provide title and body in the format: create issue [title] with body [body] in repo [name]"))
                else:
                    yield RunYield(message=create_text_response("Please provide title and body in the format: create issue [title] with body [body] in repo [name]"))
                
            elif "review pr" in command or "check pull request" in command:
                parts = command.split("in repo")
                if len(parts) != 2:
                    yield RunYield(message=create_text_response("Please specify the repository name with 'in repo [name]'"))
                    continue
                    
                pr_details = parts[0].replace("review pr", "").replace("check pull request", "").strip()
                repo_name = parts[1].strip()
                
                try:
                    pr_number = int(pr_details)
                    result = agent.review_pull_request(repo_name, pr_number)
                    response_text = f"Pull request review:\n\n{json.dumps(result, indent=2)}"
                    yield RunYield(message=create_text_response(response_text))
                except ValueError:
                    yield RunYield(message=create_text_response("Please provide a valid PR number in the format: review pr [number] in repo [name]"))
                
            elif "analyze code" in command or "check code" in command:
                parts = command.split("in repo")
                if len(parts) != 2:
                    yield RunYield(message=create_text_response("Please specify the repository name with 'in repo [name]'"))
                    continue
                    
                path_details = parts[0].replace("analyze code", "").replace("check code", "").strip()
                repo_name = parts[1].strip()
                
                result = agent.analyze_code(repo_name, path_details)
                response_text = f"Code analysis:\n\n{json.dumps(result, indent=2)}"
                yield RunYield(message=create_text_response(response_text))
                
            else:
                help_text = """
                I can help you with GitHub operations. Here are the available commands:
                
                - list repos [optional search query]
                - create issue [title] with body [body] in repo [owner/name]
                - review pr [number] in repo [owner/name]
                - analyze code [path] in repo [owner/name]
                
                Please try one of these commands.
                """
                yield RunYield(message=create_text_response(help_text))
                
        except Exception as e:
            error_message = f"Error processing command: {str(e)}"
            yield RunYield(message=create_text_response(error_message))

@server.agent(metadata=Metadata(name="health", description="Health check endpoint", ui={"type": "health"}))
async def health_check(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, None]:
    """Health check endpoint for the GitHub agent."""
    yield RunYield(message=create_text_response("I'm healthy and ready to process GitHub commands!"))

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000) 