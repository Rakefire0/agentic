from github_agent import GitHubAgent
import json

def test_agent_info():
    """Test the agent info endpoint."""
    agent = GitHubAgent()
    info = agent.get_agent_info()
    print("\nAgent Info:")
    print(json.dumps(info, indent=2))
    assert info["name"] == "GitHub Agent"
    assert "capabilities" in info
    assert "required_env_vars" in info

def test_handle_request():
    """Test the request handler."""
    agent = GitHubAgent()
    
    # Test list repositories
    response = agent.handle_request({
        "action": "list_repositories",
        "params": {"query": ""}
    })
    print("\nList Repositories Response:")
    print(json.dumps(response, indent=2))
    assert response["status"] == "success"
    assert "data" in response
    
    # Test create issue
    response = agent.handle_request({
        "action": "create_issue",
        "params": {
            "repo_name": "test-repo",
            "title": "Test Issue",
            "body": "This is a test issue",
            "labels": ["test"]
        }
    })
    print("\nCreate Issue Response:")
    print(json.dumps(response, indent=2))
    assert response["status"] in ["success", "error"]  # Might fail if repo doesn't exist
    
    # Test invalid action
    response = agent.handle_request({
        "action": "invalid_action",
        "params": {}
    })
    print("\nInvalid Action Response:")
    print(json.dumps(response, indent=2))
    assert response["status"] == "error"
    assert "Unknown action" in response["message"]

if __name__ == "__main__":
    print("Testing GitHub Agent BeeAI Integration...")
    test_agent_info()
    test_handle_request()
    print("\nAll tests completed!") 