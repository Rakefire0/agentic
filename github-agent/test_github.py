from github import Github
import os

def test_github():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Please set GITHUB_TOKEN environment variable")
        return
    
    g = Github(token)
    user = g.get_user()
    print(f"Successfully connected as {user.login}")
    print("Repositories:")
    for repo in user.get_repos():
        print(f"- {repo.name}")

if __name__ == "__main__":
    test_github()
