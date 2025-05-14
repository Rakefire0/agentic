from pydantic_settings import BaseSettings
from typing import Optional

class GitHubAgentConfig(BaseSettings):
    """Configuration settings for the GitHub agent."""
    github_token: str
    default_repo: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour

    class Config:
        env_prefix = "GITHUB_AGENT_" 