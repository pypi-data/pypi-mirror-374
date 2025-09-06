import anyio
from rich import print

from daydream.agent.utils import get_agents
from daydream.cli.agent._app import agent_app
from daydream.cli.options import PROFILE_OPTION


@agent_app.command()
def list(profile: str = PROFILE_OPTION) -> None:
    """List the available agents."""

    async def _run() -> None:
        print("Available agents:")
        for agent in sorted(get_agents(profile)):
            print(f"* {agent}")

    anyio.run(_run)
