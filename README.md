# BeeAI GitHub Agent

A powerful GitHub integration agent for BeeAI that enables automated GitHub operations with chain-of-thought reasoning capabilities.

## Features

- Repository management
- Issue creation and tracking
- Pull request review and analysis
- Code analysis and insights
- Natural language command processing
- Chain-of-thought reasoning for complex tasks

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
```bash
export GITHUB_AGENT_GITHUB_TOKEN="your_github_token"
export GITHUB_AGENT_DEFAULT_REPO="your_default_repo"  # Optional
```

## Usage

```python
from github_agent import GitHubAgent
from config import GitHubAgentConfig

# Initialize the agent
config = GitHubAgentConfig()
agent = GitHubAgent(config.github_token)

# List repositories
repos = agent.list_repositories()

# Create an issue
issue = agent.create_issue(
    repo_name="your-repo",
    title="New Feature Request",
    body="Please implement this feature",
    labels=["enhancement"]
)

# Review a pull request
review = agent.review_pull_request(
    repo_name="your-repo",
    pr_number=123
)

# Process natural language commands
result = agent.process_command("Create a new issue about implementing dark mode")
```

## Integration with BeeAI

The GitHub agent is designed to work seamlessly with the BeeAI framework. It can be used to:

1. Automate GitHub workflows
2. Analyze code and provide insights
3. Manage issues and pull requests
4. Perform complex operations with chain-of-thought reasoning

## Security

- Never commit your GitHub token to version control
- Use environment variables for sensitive information
- Implement proper access controls in your BeeAI application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 