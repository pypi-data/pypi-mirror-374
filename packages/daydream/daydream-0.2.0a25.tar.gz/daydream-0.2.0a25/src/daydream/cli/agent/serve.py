import os

import anyio
import typer

from daydream.agent.app import listen, settings
from daydream.cli.agent._app import agent_app


@agent_app.command()
def serve(
    host: str = typer.Option(settings.DAYDREAM_HOST, help="The host to bind to"),
    port: int = typer.Option(settings.DAYDREAM_PORT, help="The port to bind to"),
    workers: int = typer.Option(settings.DAYDREAM_WORKERS, help="The number of workers to use"),
    profile: str = typer.Option(settings.DAYDREAM_PROFILE, help="The profile to use"),
    reload: bool = typer.Option(
        settings.DAYDREAM_RELOAD, help="Reload the server when the code changes"
    ),
    tunnel: bool = typer.Option(settings.DAYDREAM_TUNNEL, help="Tunnel the server through ngrok"),
    ngrok_token: str = typer.Option(
        os.getenv("NGROK_TOKEN"),
        help="The ngrok token to use to tunnel the server",
        show_default=False,
    ),
    ngrok_domain: str = typer.Option(
        settings.NGROK_DOMAIN, help="The ngrok domain to use to tunnel the server"
    ),
) -> None:
    """Run the Daydream Agent server, which loads all agents and routes between them. This is intended to be a webhook receiver for PagerDuty."""

    async def _serve() -> None:
        await listen(
            host=host,
            port=port,
            workers=workers,
            profile=profile,
            tunnel=tunnel,
            ngrok_token=ngrok_token,
            ngrok_domain=ngrok_domain,
            reload=reload,
        )

    anyio.run(_serve)
