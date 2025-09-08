"""
Configuration settings
"""

from enum import Enum

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_settings(
    pth_env: Path | None = None,
    case_sensitive: bool = True,
    extra: str = "ignore",
):
    """Load environment variables from a file.

    Args:
        pth_env: The path to the environment file. If not provided, the current working directory will be used.
        case_sensitive: Whether to treat environment variables as case-sensitive.
        extra: Whether to allow extra environment variables. See `pydantic_settings.SettingsConfigDict` for more details.
    """
    if pth_env is None:
        pth_env = Path.cwd() / ".env"

    class Settings(BaseSettings):
        """Docker settings with environment variables support."""

        model_config = SettingsConfigDict(
            env_file=pth_env if pth_env.exists() else None,
            env_file_encoding="utf-8" if pth_env.exists() else None,
            case_sensitive=case_sensitive,
            extra=extra,
        )

        REPOSITORY: str = Field(description="The repository of the project")
        PROJECT_NAME: str = Field(description="The project name of the project")
        VERSION: str = Field(description="The version of the project")
        APPLICATION: str = Field(description="The application of the project")

    return Settings()


class Extra(str, Enum):
    """Extra settings (for `typer`; ideally Literal[...])"""

    ALLOW = "allow"
    IGNORE = "ignore"
    FORBID = "forbid"
