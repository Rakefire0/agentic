# GitHub Agent Deployment Instructions

This guide will walk you through setting up the GitHub Agent on a new MacBook. The agent allows you to interact with GitHub repositories using natural language commands.

## Prerequisites

- macOS (tested on macOS Monterey or newer)
- Python 3.9+ installed
- Git installed
- GitHub account with personal access token
- InstructLab or other LLM API access

## Step 1: Clone the Repository

```bash
# Create a projects directory (optional)
mkdir -p ~/AI\ Projects
cd ~/AI\ Projects

# Clone the repository (use your actual repository URL)
git clone https://github.com/yourusername/github-granite-agent.git
cd github-granite-agent
```

## Step 2: Set Up a Python Virtual Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

## Step 3: Install Dependencies

```bash
# Install required packages
pip install beeai-framework PyGithub python-dotenv requests
```

## Step 4: Create Environment Variables File

Create a `.env` file in the project root:

```bash
touch .env
```

Edit the `.env` file and add the following variables:

```
GITHUB_ACCESS_TOKEN=your_github_personal_access_token
GITHUB_REPOSITORY=username/repository_name
INSTRUCTLAB_URL=http://127.0.0.1:8000/v1
GRANITE_MODEL=granite-7b-lab-Q4_K_M
```

Replace:
- `your_github_personal_access_token` with your GitHub personal access token
- `username/repository_name` with the repository you want to manage (e.g., `Rakefire0/notifications`)

## Step 5: Set Up InstructLab (IBM Granite Model Server)

Follow the InstructLab installation instructions. For the local setup:

1. Install InstructLab CLI:
   ```bash
   pip install instructlab
   ```

2. Pull the Granite model:
   ```bash
   ilab model pull granite-7b-lab-Q4_K_M
   ```

3. You'll need to start the InstructLab server before running the GitHub agent.

## Step 6: Create the GitHub Agent Script

Create a directory for the agent and the main script:

```bash
mkdir -p granite_agent
cd granite_agent
touch github_agent.py
```

Copy and paste the full GitHub agent code into `github_agent.py`.

## Step 7: Running the GitHub Agent

To run the agent:

1. First, make sure the InstructLab server is running in a separate terminal:
   ```bash
   ilab model serve --model granite-7b-lab-Q4_K_M --port 8000
   ```

2. In a separate terminal, activate your virtual environment and run the GitHub agent:
   ```bash
   cd ~/AI\ Projects/github-granite-agent
   source .venv/bin/activate
   python granite_agent/github_agent.py
   ```

The agent will initialize, connect to GitHub, and present a REPL interface where you can enter commands.

## Example Commands

Once the agent is running, try these commands:

```
show me repository information
how many issues are there?
create a new issue with the title of "Bug Report" and then create the text for the issue based on the title
close issue 1
```

## Troubleshooting

1. **GitHub Access Issues**:
   - Ensure your GitHub token has the necessary permissions (repo, issues, etc.)
   - Verify the repository exists and is accessible with your token

2. **InstructLab Connection Issues**:
   - Confirm InstructLab server is running on the specified port
   - Check that the model is properly downloaded

3. **Python Environment Issues**:
   - Make sure all dependencies are installed
   - Verify you're using Python 3.9 or newer

## Customization

You can customize the GitHub agent by:

1. **Changing the system prompt** - Edit the `system_prompt` variable in the `main()` function
2. **Adding more tools** - Implement additional GitHub functionality in new tool classes
3. **Modifying pattern matching** - Enhance the regex patterns in `process_query_directly`

## Updating

To update the GitHub agent:

1. Pull the latest changes:
   ```bash
   git pull origin main
   ```

2. Update dependencies if needed:
   ```bash
   pip install -r requirements.txt
   ```

Enjoy using your GitHub agent to easily manage your repositories!
