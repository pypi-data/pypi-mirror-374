import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from pydantic_settings import BaseSettings
from rich import print
from uvicorn.supervisors import ChangeReload, Multiprocess

from daydream.agent.analysis import AnalysisAgent
from daydream.config.utils import get_config_dir


class Settings(BaseSettings):
    NGROK_TOKEN: str = ""
    NGROK_DOMAIN: str = ""

    DAYDREAM_TUNNEL: bool = False
    DAYDREAM_RELOAD: bool = False
    DAYDREAM_PROFILE: str = "default"
    DAYDREAM_HOST: str = "127.0.0.1"
    DAYDREAM_PORT: int = 8000
    DAYDREAM_WORKERS: int = 1


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    tunnel = settings.DAYDREAM_TUNNEL
    ngrok_domain = settings.NGROK_DOMAIN
    ngrok_token = settings.NGROK_TOKEN
    host = settings.DAYDREAM_HOST
    port = settings.DAYDREAM_PORT
    internal_url = f"http://{host}:{port}/webhook"
    external_url = None

    if tunnel:
        from pyngrok import ngrok

        ngrok.set_auth_token(ngrok_token)
        listener = ngrok.connect(
            addr=f"{host}:{port}", name=f"daydream-{port}", domain=ngrok_domain
        )
        external_url = f"{listener.public_url}/webhook"
        print(f"Tunnel opened: {external_url} -> {internal_url}")

        try:
            yield
        finally:
            print(f"Closing tunnel {external_url}")
            ngrok.kill()
    else:
        yield


app = FastAPI(lifespan=lifespan)
app.state.analysis_tasks = set()


async def analyze(payload: dict[str, Any], profile: str) -> None:
    analysis_agent = AnalysisAgent(profile)
    analysis = await analysis_agent.acall(payload=payload)
    print(analysis)


@app.post("/webhook")
async def webhook(request: Request) -> dict[str, Any]:
    analysis_tasks = request.app.state.analysis_tasks

    # Extract the alert payload from the request.
    payload = await request.json()

    # Start a background task to analyze the payload.
    task = asyncio.create_task(analyze(payload, settings.DAYDREAM_PROFILE))

    # Add task to the set to create a strong reference.
    analysis_tasks.add(task)

    # Remove the task from the set when it completes to avoid memory leaks.
    task.add_done_callback(analysis_tasks.discard)

    return {"message": "OK"}


async def listen(
    host: str = "127.0.0.1",
    port: int = 8000,
    workers: int = 1,
    profile: str = "default",
    reload: bool = False,
    tunnel: bool = False,
    ngrok_token: str = "",
    ngrok_domain: str = "",
) -> None:
    # Set environment variables to make them accessible to FastAPI's lifespan.
    settings.DAYDREAM_PROFILE = profile
    settings.DAYDREAM_TUNNEL = tunnel
    settings.NGROK_TOKEN = ngrok_token
    settings.NGROK_DOMAIN = ngrok_domain
    settings.DAYDREAM_HOST = host
    settings.DAYDREAM_PORT = port

    # Recurse up the directory tree until we find the pyproject.toml file (i.e.,
    # the project root).
    reload_config = {}
    if reload:
        project_root = Path(__file__).parent
        while "__version__" not in (project_root / "__init__.py").read_text():
            project_root = project_root.parent
            if not project_root.exists():
                raise FileNotFoundError("Could not find the project root")
        reload_config = {
            "reload": True,
            "reload_dirs": [str(project_root), str(get_config_dir(profile))],
            "reload_includes": ["**/*.py", "**/*.yaml"],
        }

    uvicorn_config = uvicorn.Config(
        f"{__name__}:app",
        host=host,
        port=port,
        workers=workers,
        ws="none",
        **reload_config,
    )

    server = uvicorn.Server(config=uvicorn_config)

    try:
        if uvicorn_config.should_reload:
            sock = uvicorn_config.bind_socket()
            ChangeReload(uvicorn_config, target=server.run, sockets=[sock]).run()
        elif uvicorn_config.workers > 1:
            sock = uvicorn_config.bind_socket()
            Multiprocess(uvicorn_config, target=server.run, sockets=[sock]).run()
        else:
            await server.serve()
    except KeyboardInterrupt:
        pass  # pragma: full coverage
    finally:
        uds = Path(uvicorn_config.uds) if uvicorn_config.uds else None
        if uds and uds.exists():
            uds.unlink()  # pragma: py-win32

    if not server.started and not uvicorn_config.should_reload and uvicorn_config.workers == 1:
        sys.exit(3)
