from github_agent import GitHubAgent
import os
from dotenv import load_dotenv

def test_github_connection():
    """Test the GitHub connection and basic functionality."""
    try:
        # Initialize the agent
        agent = GitHubAgent()
        
        # Test listing repositories
        print("\nTesting repository listing...")
        repos = agent.list_repositories()
        print(f"Found {len(repos)} repositories")
        for repo in repos[:3]:  # Show first 3 repos
            print(f"- {repo['name']}: {repo['url']}")
            
        # Test default repo if configured
        default_repo = os.getenv('GITHUB_AGENT_DEFAULT_REPO')
        if default_repo:
            print(f"\nTesting default repository access: {default_repo}")
            try:
                repo_info = agent.analyze_code(default_repo)
                print(f"Repository info: {repo_info}")
            except Exception as e:
                print(f"Error accessing default repo: {str(e)}")
        
        print("\nGitHub agent configuration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError testing GitHub agent: {str(e)}")
        return False

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check if GitHub token is set
    if not os.getenv('GITHUB_AGENT_GITHUB_TOKEN'):
        print("Error: GITHUB_AGENT_GITHUB_TOKEN not found in environment variables")
        print("Please set it in your .env file")
    else:
        test_github_connection() 