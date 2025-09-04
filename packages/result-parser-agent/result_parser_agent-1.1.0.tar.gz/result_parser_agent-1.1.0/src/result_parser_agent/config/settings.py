"""Configuration management for the results parser agent."""

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, Field

# Explicitly load .env from current working directory
load_dotenv()


class APIConfig(BaseSettings):
    """API configuration class for the results parser agent."""

    PARSER_REGISTRY_URL: str = Field(default="http://10.138.172.118:8001")
    PARSER_REGISTRY_TIMEOUT: int = Field(default=30)


class ParserConfig(BaseSettings):
    """Unified configuration class for the results parser agent."""

    # Script Downloader Configuration
    SCRIPTS_BASE_URL: str = Field(
        default="git@github.com:AMD-DEAE-CEME/epdw2.0_parser_scripts.git",
        description="SSH git URL for the scripts repository",
    )
    SCRIPTS_CACHE_DIR: str = Field(
        default="~/.cache/result-parser/scripts",
        description="Local directory to cache downloaded scripts",
    )
    SCRIPTS_CACHE_TTL: int = Field(
        default=3600, description="Script cache TTL in seconds (1 hour)"
    )

    # Environment variable settings
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = ParserConfig()
