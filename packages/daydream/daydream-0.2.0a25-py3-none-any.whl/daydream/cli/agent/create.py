import os

import anyio
import typer
from rich import print

from daydream.cli.agent._app import agent_app
from daydream.cli.agent.actions import create_agent
from daydream.cli.options import PROFILE_OPTION
from daydream.utils import edit_file


@agent_app.command()
def create(
    agent_name: str = typer.Argument(..., help="The name of the agent to create"),
    profile: str = PROFILE_OPTION,
    overwrite: bool = typer.Option(False, help="Overwrite the agent file if it already exists"),
    template: str = typer.Option("default", help="The template to use to create the agent file"),
    editor: str = typer.Option(
        os.environ.get("EDITOR"), help="The editor to use to open the agent file"
    ),
    no_edit: bool = typer.Option(False, help="Do not open the agent file in your editor"),
) -> None:
    """Create a new agent configuration file and open it in your editor."""

    async def _create() -> None:
        agent_file = create_agent(
            agent_name=agent_name,
            profile=profile,
            overwrite=overwrite,
            template=template,
        )
        # Open the file in the user's editor
        if editor and not no_edit:
            try:
                await edit_file(agent_file, editor)
            except ValueError as ex:
                print(
                    "[red]No editor specified. Set the $EDITOR environment variable or use --editor option.[/red]"
                )
                print(f"[blue]Please manually open {str(agent_file)!r} in your editor.[/blue]")
                raise typer.Exit() from ex

    anyio.run(_create)
