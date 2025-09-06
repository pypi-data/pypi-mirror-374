import os
import warnings
from pathlib import Path

import pydantic.warnings
from pydantic_yaml import parse_yaml_file_as

from daydream.agent.analysis import Agent
from daydream.config.utils import get_config_dir

TEMPLATE_DIR = Path(__file__).parent / "templates"


warnings.filterwarnings(
    "ignore",
    category=pydantic.warnings.PydanticDeprecatedSince20,
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message="The request_id parameter is deprecated from the (?:\\S+) API and will be removed in a future version. Please use the `trace_id` parameter instead.",
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message="There is no current event loop",
)


if os.environ.get("MLFLOW_TRACKING_URI"):
    import logging

    import mlflow

    mlflow_logger = logging.getLogger("mlflow")
    mlflow_logger.setLevel(logging.WARNING)
    print("> daydream: Found MLFLOW_TRACKING_URI environment variable, running `mlflow.autolog()`")
    mlflow.autolog()
    mlflow.set_experiment("Daydream Agent")


def get_agent_templates() -> list[str]:
    """Get the contents of the agent template for the given agent name."""
    return [
        str(template_file.relative_to(TEMPLATE_DIR).with_suffix(""))
        for template_file in TEMPLATE_DIR.glob("**/*.yaml")
    ]


def get_agent_template(agent_name: str) -> str:
    """Get the contents of the agent template for the given agent name."""
    return (Path(__file__).parent / "templates" / f"{agent_name}.yaml").read_text()


def get_agents(profile: str) -> list[str]:
    """Get the names of the agents in the config directory."""
    agents_dir = get_config_dir(profile, create=False) / "agents"
    return [
        str(agent_file.relative_to(agents_dir).with_suffix(""))
        for agent_file in agents_dir.glob("**/*.yaml")
    ]


def load_agent(agent_name: str, profile: str) -> Agent:
    """Load the agent with the given name from the profile."""
    agent_file = get_config_dir(profile, create=False) / "agents" / f"{agent_name}.yaml"

    # If they're trying to load the default agent and it doesn't exist, create it.
    if not agent_file.exists() and agent_name == "default":
        agent_file.parent.mkdir(parents=True, exist_ok=True)
        agent_file.touch()
        agent_file.write_text(get_agent_template(agent_name))

    return parse_yaml_file_as(Agent, agent_file)


def delete_agent(agent_name: str, profile: str) -> None:
    """Delete the agent with the given name from the profile."""
    agent_file = get_config_dir(profile, create=False) / "agents" / f"{agent_name}.yaml"
    agent_file.unlink()
