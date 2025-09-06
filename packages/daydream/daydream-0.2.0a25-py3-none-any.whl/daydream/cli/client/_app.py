import typer

from daydream.cli.client.logs.app import client_logs_app

client_app = typer.Typer(help="Work with clients of the Daydream MCP Server", no_args_is_help=True)
client_app.add_typer(client_logs_app, name="logs")
