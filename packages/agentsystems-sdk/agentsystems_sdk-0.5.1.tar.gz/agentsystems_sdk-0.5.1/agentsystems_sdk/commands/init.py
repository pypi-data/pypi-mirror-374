"""Initialize a new AgentSystems project."""

from __future__ import annotations

import pathlib
import re
import shutil
import sys
import uuid
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from dotenv import set_key

from ..utils import (
    ensure_docker_installed,
    run_command,
    get_required_images,
)

console = Console()


def init_command(
    project_dir: Optional[pathlib.Path] = typer.Argument(
        None,
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
) -> None:
    """Initialize a new AgentSystems deployment from the built-in template.

    Steps:
    1. Copy the deployment template to *project_dir*.
    2. Pull Docker images required by the platform.
    """
    # Determine target directory
    if project_dir is None:
        if not sys.stdin.isatty():
            typer.secho(
                "TARGET_DIR argument required when running non-interactively.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
        default_name = "agent-platform-deployments"
        dir_input = typer.prompt("Directory to create", default=default_name)
        project_dir = pathlib.Path(dir_input)
        if not project_dir.is_absolute():
            project_dir = pathlib.Path.cwd() / project_dir

    project_dir = project_dir.expanduser()
    if project_dir.exists() and any(project_dir.iterdir()):
        typer.secho(
            f"Directory {project_dir} is not empty – aborting.", fg=typer.colors.RED
        )
        raise typer.Exit(code=1)

    # Prompt for missing tokens only if running interactively

    # ---------- Langfuse initial setup prompts ----------
    if sys.stdin.isatty():
        console.print("\n[bold cyan]Langfuse initial setup[/bold cyan]")

        org_name = typer.prompt("Organization name", default="ExampleOrg")
        org_id = re.sub(r"[^a-z0-9]+", "-", org_name.lower()).strip("-") or "org"
        project_id = "default"
        project_name = "Default"
        user_name = "Admin"

        while True:
            email = typer.prompt("Set Langfuse admin email")
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                break
            console.print("[red]Please enter a valid email address.[/red]")

        while True:
            password = typer.prompt(
                "Set Langfuse admin password (min 8 chars)", hide_input=True
            )
            if len(password) >= 8:
                break
            console.print("[red]Password must be at least 8 characters.[/red]")

        pub_key = f"pk-lf-{uuid.uuid4()}"
        secret_key = f"sk-lf-{uuid.uuid4()}"
    else:
        org_name = "ExampleOrg"
        org_id = "org"
        project_id = "default"
        project_name = "Default"
        user_name = "Admin"
        email = ""
        password = ""
        pub_key = f"pk-lf-{uuid.uuid4()}"
        secret_key = f"sk-lf-{uuid.uuid4()}"

    # Get the path to the scaffold directory
    import os

    scaffold_dir = (
        pathlib.Path(os.path.dirname(__file__)).parent / "deployments_scaffold"
    )

    if not scaffold_dir.exists():
        typer.secho(
            "Error: Deployment scaffold not found. Please reinstall agentsystems-sdk.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    # ---------- UI banner ----------
    console.print(
        Panel.fit(
            "🚀 [bold cyan]AgentSystems SDK[/bold cyan] – initialization",
            border_style="bright_cyan",
        )
    )

    # ---------- Progress ----------
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold]{task.description}"),
        BarColumn(style="bright_magenta"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        # Copy template
        copy_task = progress.add_task("Copying deployment template", total=None)

        try:
            shutil.copytree(scaffold_dir, project_dir)
            progress.update(copy_task, completed=1)
        except Exception as e:
            typer.secho(
                f"Failed to copy template: {e}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

        # ---------- Write Langfuse .env ----------
        env_example = project_dir / ".env.example"
        env_file = project_dir / ".env"
        if env_example.exists() and not env_file.exists():
            shutil.copy(env_example, env_file)
            env_file = project_dir / ".env"
        else:
            env_file = env_file if env_file.exists() else env_example

        cfg_pairs = {
            "LANGFUSE_INIT_ORG_ID": org_id,
            "LANGFUSE_INIT_ORG_NAME": org_name,
            "LANGFUSE_INIT_PROJECT_ID": project_id,
            "LANGFUSE_INIT_PROJECT_NAME": project_name,
            "LANGFUSE_INIT_USER_NAME": user_name,
            "LANGFUSE_INIT_USER_EMAIL": email,
            "LANGFUSE_INIT_USER_PASSWORD": password,
            "LANGFUSE_INIT_PROJECT_PUBLIC_KEY": pub_key,
            "LANGFUSE_INIT_PROJECT_SECRET_KEY": secret_key,
            # Runtime vars (must be *unquoted* for Docker)
            "LANGFUSE_HOST": "http://langfuse-web:3000",
            "LANGFUSE_PUBLIC_KEY": pub_key,
            "LANGFUSE_SECRET_KEY": secret_key,
        }

        for k, v in cfg_pairs.items():
            # Quote only the one-shot INIT vars; runtime vars stay raw
            value_to_write = f'"{v}"' if k.startswith("LANGFUSE_INIT_") else str(v)
            set_key(str(env_file), k, value_to_write, quote_mode="never")

        # Check Docker
        docker_task = progress.add_task("Checking Docker", total=1)
        ensure_docker_installed()
        progress.update(docker_task, completed=1)

        # Pull required images
        required_images = get_required_images()

        if not required_images:
            # No images configured for pulling during init - this is expected
            # Images will be pulled automatically during 'agentsystems up' instead
            pass
        else:
            pull_task = progress.add_task(
                "Pulling Docker images", total=len(required_images)
            )

            for img in required_images:
                progress.update(pull_task, description=f"Pulling {img}")
                progress.stop()  # Stop progress to show docker output
                try:
                    run_command(["docker", "pull", img])
                except typer.Exit:
                    # Image pull failed - control-plane is public on ghcr.io
                    # This shouldn't happen unless there's a network issue
                    raise
                finally:
                    progress.start()  # Always restart progress
                progress.advance(pull_task)

    # ---------- Completion message ----------
    display_dir = project_dir.name
    next_steps = (
        f"✅ Initialization complete!\n\n"
        f"Next steps:\n"
        f"  1. cd {display_dir}\n"
        f"  2. Run: agentsystems up\n"
        f"  3. Open http://localhost:3001 to configure this deployment\n"
    )
    console.print(Panel.fit(next_steps, border_style="green"))
