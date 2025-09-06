import typer

from daydream.cli.agent._app import agent_app
from daydream.cli.client._app import client_app
from daydream.cli.graph._app import graph_app
from daydream.cli.mlflow._app import mlflow_app
from daydream.cli.tools._app import tools_app

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)
app.add_typer(tools_app, name="tools")
app.add_typer(client_app, name="client")
app.add_typer(graph_app, name="graph")
app.add_typer(agent_app, name="agent")
app.add_typer(mlflow_app, name="mlflow")
