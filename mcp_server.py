import typing
import asyncio
from loguru import logger
from mcp.server import FastMCP
from agent.manage import Manage


# nuitka --macos-create-app-bundle --show-progress --output-dir=applications mcp_server.py
mcp = FastMCP(name="ProxyMind", json_response=True, port=3333)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
device_list = loop.run_until_complete(Manage("adb").devices())
print(device_list)


@mcp.tool()
async def tap(x: int, y: int) -> typing.Any:
    logger.info(f"Tap {x} {y}")
    return await asyncio.gather(
        *(device.tap(x, y) for device in device_list)
    )


@mcp.tool()
async def swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> typing.Any:
    logger.info(f"Swipe {x1} {y1} {x2} {y2} {duration}")
    return await asyncio.gather(
        *(device.swipe(x1, y1, x2, y2, duration) for device in device_list)
    )


@mcp.tool()
async def key_event(keycode: int) -> typing.Any:
    logger.info(f"KeyEvent {keycode}")
    return await asyncio.gather(
        *(device.key_event(keycode) for device in device_list)
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
