import sys
import signal
import asyncio
from pathlib import Path
from loguru import logger
from rich.prompt import Prompt
from mcp import (
    ClientSession, ListToolsResult
)
from mcp.client.streamable_http import streamable_http_client
from engine.manage import McpServer
from engine.terminal import Terminal
from utils import (
    craft, request
)


def signal_processor(*_, **__) -> None:
    logger.info(f"Received signal {signal.SIGINT}")
    sys.exit(0)


async def boot() -> McpServer:
    await craft.setup_logger()

    root = Path(__file__).parent

    program = Path(root, "agent", "mcp_server.py")
    # program = Path(root, "applications", "mcp_server.app", "Contents", "MacOS", "mcp_server")
    # program = Path(root, "applications", "mcp_server.dist", "mcp_server.exe")
    await Terminal.cmd_line(["chmod", "+x", program])

    return McpServer(program)


async def trip(message: str, model: str = "llama-3.3-70b-versatile") -> None:

    url = "http://127.0.0.1:3333/mcp"

    async with streamable_http_client(url) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()

            list_tools: ListToolsResult = await session.list_tools()

            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description" : tool.description,
                        "parameters"  : tool.inputSchema
                    }
                }
                for tool in list_tools.tools
            ]

            for tool in openai_tools: logger.info(f"⚙️ Tool {tool}")

            payload = {"model": model, "message": message, "tools": openai_tools}

            async for plan in request.stream_planner(payload):
                if not (steps := plan.get("steps")):
                    continue

                for step in steps:
                    action = step["action"]
                    result = await session.call_tool(action["action"], action["args"])

                    if result.content:
                        logger.info(f"Content: {result.content[0].text}")
                    elif result.structuredContent:
                        logger.info(f"StructuredContent: {result.structuredContent}")
                    elif result.isError:
                        return logger.error(f"IsError: {result.isError}")

                    await asyncio.sleep(1)


async def main() -> None:
    # nuitka --macos-create-app-bundle --show-progress --output-dir=applications agent/mcp_server.py
    # nuitka --mode=standalone --product-name=Mind --product-version=1.0.0 --windows-icon-from-ico=schematic/resources/icons/butterfly.ico --show-progress --show-memory --assume-yes-for-downloads --output-dir=applications agent/mcp_server.py
    # lsof -ti :3333 | xargs kill -9
    # Get-NetTCPConnection -LocalPort 3333 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

    server = await boot()

    await server.mcp_begin()

    signal.signal(signal.SIGINT, signal_processor)

    try:
        while (action := Prompt.ask(f"[bold #AFD7FF]🤔 Exec[/]")) != "88":
            await trip(action)
    # except Exception as e:
    #     logger.error(e)
    finally:
        await server.mcp_final()


if __name__ == '__main__':
    asyncio.run(main())
