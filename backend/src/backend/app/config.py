from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="crewAI Research Backend")
    environment: str = Field(default="development")
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])  # dev
    # Search
    search_provider: str = Field(default="ddg")  # tavily|bing|serpapi|ddg
    tavily_api_key: str | None = None
    bing_search_key: str | None = None
    bing_search_endpoint: str | None = None
    serpapi_api_key: str | None = None
    # LLM
    llm_provider: str = Field(default="none")  # openai|azure-openai|anthropic|none
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
