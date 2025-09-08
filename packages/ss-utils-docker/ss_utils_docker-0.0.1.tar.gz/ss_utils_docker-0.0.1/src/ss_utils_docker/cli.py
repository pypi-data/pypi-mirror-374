"""Command line interface for ss-utils-logging."""

import os
import subprocess
from pydantic import ValidationError
from pathlib import Path
from typing import Annotated

import typer

from .config import load_settings, Extra
from pydantic_settings import BaseSettings

HELP_TEXT_PTH_ENV = (
    "The path to the environment file. You MUST provide `*.env` file (.env, prod.env.prod, ...) OR define the following environment variables:"
    " [REPOSITORY, PROJECT_NAME, VERSION, APPLICATION]"
)
HELP_TEXT_CASE_SENSITIVE = "Whether to treat environment variables as case-sensitive"
HELP_TEXT_EXTRA = "Whether to allow extra environment variables"
HELP_TEXT_CACHE = "Whether to use cache"
HELP_TEXT_DETACHED = "Whether to run the container in detached mode"
HELP_TEXT_DRY_RUN = "Whether to just print the command to be run"

IMAGE_INFO_TEMPLATE = "Building for: {REPOSITORY}/{PROJECT_NAME}/{APPLICATION}:{VERSION}"

app = typer.Typer()


def _load_settings(
    pth_env: Path | None = None, case_sensitive: bool = True, extra: Extra = Extra.IGNORE
) -> type[BaseSettings]:
    try:
        settings = load_settings(pth_env, case_sensitive, extra)
    except ValidationError as e:
        typer.echo(f"Please check the environment variables: {e}")
        raise typer.Exit(code=1)  # noqa: B904
    return settings


def _check_docker_compose_yml():
    """Check if `docker-compose.yml` exists in the current directory.

    Raises:
        typer.Exit: If `docker-compose.yml` does not exist in the current directory.
    """
    pth_docker_compose_yml = Path("docker-compose.yml")
    if not pth_docker_compose_yml.exists():
        typer.echo(
            "`docker-compose.yml` does not exist in the current directory. Please run this command in the same directory."
        )
        raise typer.Exit(code=1)  # noqa: B904


def _run_docker_command(cmd: list[str], env_vars: dict) -> None:
    """Run docker command with real-time output streaming."""
    try:
        env = {**os.environ, **env_vars}
        process = subprocess.Popen(
            cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1
        )

        # Stream output in real-time
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                typer.echo(line.rstrip())

        process.wait()

        if process.returncode != 0:
            typer.echo(f"Command failed with return code {process.returncode}: {' '.join(cmd)}")
            raise typer.Exit(code=process.returncode)

    except Exception as e:
        typer.echo(f"Error executing command ({cmd}): {e}")
        raise typer.Exit(code=1)  # noqa: B904


@app.command("build")
def build(
    pth_env: Annotated[Path | None, typer.Argument(help=HELP_TEXT_PTH_ENV)] = None,
    case_sensitive: Annotated[bool, typer.Option(help=HELP_TEXT_CASE_SENSITIVE)] = True,
    extra: Annotated[Extra, typer.Option(help=HELP_TEXT_EXTRA)] = Extra.IGNORE,
    cache: Annotated[bool, typer.Option(help=HELP_TEXT_CACHE)] = True,
    dry_run: Annotated[bool, typer.Option(help=HELP_TEXT_DRY_RUN)] = False,
):
    """Run `docker compose build` with the given settings.
    Builds the image: `${REPOSITORY}/${PROJECT_NAME}/${APPLICATION}:${VERSION}`

    `docker-compose.yml` MUST be in the current directory.
    """
    _check_docker_compose_yml()
    settings = _load_settings(pth_env, case_sensitive, extra)
    env_vars = settings.model_dump()

    typer.echo(IMAGE_INFO_TEMPLATE.format(**settings.model_dump()))
    cmd = ["docker", "compose", "build"]
    if not cache:
        cmd.append("--no-cache")

    if dry_run:
        typer.echo(f"Command: {' '.join(cmd)}")
        return
    _run_docker_command(cmd, env_vars)


@app.command("up")
def up(
    detached: Annotated[bool, typer.Option("--detached", "-d", help=HELP_TEXT_DETACHED)] = False,
    pth_env: Annotated[Path | None, typer.Argument(help=HELP_TEXT_PTH_ENV)] = None,
    case_sensitive: Annotated[bool, typer.Option(help=HELP_TEXT_CASE_SENSITIVE)] = True,
    extra: Annotated[Extra, typer.Option(help=HELP_TEXT_EXTRA)] = Extra.IGNORE,
    dry_run: Annotated[bool, typer.Option(help=HELP_TEXT_DRY_RUN)] = False,
):
    """Run `docker compose up` with the given settings."""
    _check_docker_compose_yml()
    settings = _load_settings(pth_env, case_sensitive, extra)
    env_vars = settings.model_dump()

    typer.echo(IMAGE_INFO_TEMPLATE.format(**settings.model_dump()))
    cmd = ["docker", "compose", "up"]
    if detached:
        cmd.append("-d")
    if dry_run:
        typer.echo(f"Command: {' '.join(cmd)}")
        return
    _run_docker_command(cmd, env_vars)


@app.command("down")
def down(
    pth_env: Annotated[Path | None, typer.Argument(help=HELP_TEXT_PTH_ENV)] = None,
    case_sensitive: Annotated[bool, typer.Option(help=HELP_TEXT_CASE_SENSITIVE)] = True,
    extra: Annotated[Extra, typer.Option(help=HELP_TEXT_EXTRA)] = Extra.IGNORE,
    dry_run: Annotated[bool, typer.Option(help=HELP_TEXT_DRY_RUN)] = False,
):
    """Run `docker compose down` with the given settings."""
    _check_docker_compose_yml()
    settings = _load_settings(pth_env, case_sensitive, extra)
    env_vars = settings.model_dump()

    typer.echo(IMAGE_INFO_TEMPLATE.format(**settings.model_dump()))
    cmd = ["docker", "compose", "down"]
    if dry_run:
        typer.echo(f"Command: {' '.join(cmd)}")
        return
    _run_docker_command(cmd, env_vars)


@app.command("push")
def push(
    pth_env: Annotated[
        Path | None,
        typer.Argument(help=HELP_TEXT_PTH_ENV),
    ] = None,
    case_sensitive: Annotated[bool, typer.Option(help=HELP_TEXT_CASE_SENSITIVE)] = True,
    extra: Annotated[Extra, typer.Option(help=HELP_TEXT_EXTRA)] = Extra.IGNORE,
    dry_run: Annotated[bool, typer.Option(help=HELP_TEXT_DRY_RUN)] = False,
):
    """Run `docker compose push` with the given settings.
    Pushes the image: `${REPOSITORY}/${PROJECT_NAME}/${APPLICATION}:${VERSION}`

    `docker-compose.yml` MUST be in the current directory.
    """
    _check_docker_compose_yml()
    settings = _load_settings(pth_env, case_sensitive, extra)
    env_vars = settings.model_dump()

    typer.echo(IMAGE_INFO_TEMPLATE.format(**settings.model_dump()))
    cmd = ["docker", "compose", "push"]
    if dry_run:
        typer.echo(f"Command: {' '.join(cmd)}")
        return
    _run_docker_command(cmd, env_vars)


if __name__ == "__main__":
    app()
