import streamlit as st
from github_agent import GitHubAgent
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize session state
if 'github_agent' not in st.session_state:
    try:
        st.session_state.github_agent = GitHubAgent()
    except ValueError as e:
        st.error(str(e))
        st.stop()

def display_repository_list():
    """Display list of repositories."""
    st.subheader("Your Repositories")
    repos = st.session_state.github_agent.list_repositories()
    
    # Add search functionality
    search_query = st.text_input("Search repositories", "")
    if search_query:
        repos = [repo for repo in repos if search_query.lower() in repo['name'].lower()]
    
    # Display repositories in a grid
    cols = st.columns(3)
    for idx, repo in enumerate(repos):
        with cols[idx % 3]:
            st.markdown(f"### [{repo['name']}]({repo['url']})")
            if st.button("View Details", key=f"view_{repo['name']}"):
                st.session_state.selected_repo = repo['name']
                st.session_state.current_view = "repo_details"

def display_repo_details():
    """Display repository details and actions."""
    st.subheader(f"Repository: {st.session_state.selected_repo}")
    
    # Back button
    if st.button("← Back to Repositories"):
        st.session_state.current_view = "repo_list"
        st.rerun()
    
    # Repository actions
    action = st.selectbox(
        "Select Action",
        ["View Issues", "Create Issue", "Review PR", "Analyze Code"]
    )
    
    if action == "View Issues":
        st.info("Issue viewing functionality coming soon!")
    
    elif action == "Create Issue":
        with st.form("create_issue"):
            title = st.text_input("Issue Title")
            body = st.text_area("Issue Description")
            labels = st.multiselect(
                "Labels",
                ["bug", "enhancement", "documentation", "question"]
            )
            
            if st.form_submit_button("Create Issue"):
                try:
                    result = st.session_state.github_agent.create_issue(
                        st.session_state.selected_repo,
                        title,
                        body,
                        labels
                    )
                    st.success(f"Issue created successfully! [View Issue]({result['url']})")
                except Exception as e:
                    st.error(f"Error creating issue: {str(e)}")
    
    elif action == "Review PR":
        pr_number = st.number_input("Pull Request Number", min_value=1, step=1)
        if st.button("Review PR"):
            try:
                review = st.session_state.github_agent.review_pull_request(
                    st.session_state.selected_repo,
                    pr_number
                )
                st.json(review)
            except Exception as e:
                st.error(f"Error reviewing PR: {str(e)}")
    
    elif action == "Analyze Code":
        path = st.text_input("Path to analyze (leave empty for root)", "")
        if st.button("Analyze"):
            try:
                analysis = st.session_state.github_agent.analyze_code(
                    st.session_state.selected_repo,
                    path
                )
                st.json(analysis)
            except Exception as e:
                st.error(f"Error analyzing code: {str(e)}")

def main():
    st.title("BeeAI GitHub Agent")
    
    # Initialize current view if not set
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "repo_list"
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        if st.button("Refresh GitHub Connection"):
            try:
                st.session_state.github_agent = GitHubAgent()
                st.success("Connection refreshed!")
            except Exception as e:
                st.error(f"Error refreshing connection: {str(e)}")
    
    # Main content
    if st.session_state.current_view == "repo_list":
        display_repository_list()
    elif st.session_state.current_view == "repo_details":
        display_repo_details()

if __name__ == "__main__":
    main() 