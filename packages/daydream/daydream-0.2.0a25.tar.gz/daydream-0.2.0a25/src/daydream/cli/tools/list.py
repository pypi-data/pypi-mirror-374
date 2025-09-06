import anyio

from daydream.cli.options import PROFILE_OPTION
from daydream.cli.tools._app import tools_app
from daydream.config import load_config
from daydream.config.utils import get_config_dir
from daydream.knowledge import Graph
from daydream.mcp import Context, build_mcp_server
from daydream.plugins import PluginManager


@tools_app.command("list")
def list_tools(
    profile: str = PROFILE_OPTION,
) -> None:
    """List all MCP tools available from enabled plugins."""

    async def _list_tools() -> None:
        config = load_config(profile)
        plugins = PluginManager(config=config)
        context = Context(
            profile=profile,
            config=config,
            plugins=plugins,
            graph=Graph(get_config_dir(profile) / "graph.json"),
        )
        mcp = await build_mcp_server(context)

        tools = await mcp.get_tools()
        for key, tool in tools.items():
            cmd = [key]
            for arg, arg_data in tool.parameters["properties"].items():
                arg_type = arg_data.get("type", "unknown")
                if "anyOf" in arg_data:
                    arg_type = "|".join(t["type"] for t in arg_data["anyOf"])
                cmd.append(f"<{arg}:{arg_type}>")
            print(" ".join(cmd))

    anyio.run(_list_tools)
