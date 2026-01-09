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
    """在所有已连接设备上点击指定的屏幕绝对坐标。"""
    logger.info(f"Tap {x} {y}")
    return await asyncio.gather(
        *(device.tap(x, y) for device in device_list)
    )


@mcp.tool()
async def swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> typing.Any:
    """在所有已连接设备上从 (x1, y1) 滑动到 (x2, y2)。"""
    logger.info(f"Swipe {x1} {y1} {x2} {y2} {duration}")
    return await asyncio.gather(
        *(device.swipe(x1, y1, x2, y2, duration) for device in device_list)
    )


@mcp.tool()
async def key_event(keycode: int) -> typing.Any:
    """向所有已连接设备发送 Android keyevent 按键码。"""
    logger.info(f"KeyEvent {keycode}")
    return await asyncio.gather(
        *(device.key_event(keycode) for device in device_list)
    )


@mcp.tool()
async def click_text(text: str, contains: bool = False) -> typing.Any:
    """点击第一个 text 匹配（或包含）给定值的控件。"""
    logger.info(f"Click text {text} contains={contains}")
    return await asyncio.gather(
        *(device.click_by_text(text, contains=contains) for device in device_list)
    )


@mcp.tool()
async def click_resource_id(resource_id: str, contains: bool = False) -> typing.Any:
    """点击第一个 resource-id 匹配（或包含）给定值的控件。"""
    logger.info(f"Click resource-id {resource_id} contains={contains}")
    return await asyncio.gather(
        *(device.click_by_resource_id(resource_id, contains=contains) for device in device_list)
    )


@mcp.tool()
async def click_desc(content_desc: str, contains: bool = False) -> typing.Any:
    """点击第一个 content-desc 匹配（或包含）给定值的控件。"""
    logger.info(f"Click content-desc {content_desc} contains={contains}")
    return await asyncio.gather(
        *(device.click_by_desc(content_desc, contains=contains) for device in device_list)
    )


@mcp.tool()
async def send_keys(text: str) -> typing.Any:
    """向所有已连接设备当前聚焦的输入框发送文本。"""
    logger.info(f"Send keys {text}")
    return await asyncio.gather(
        *(device.send_keys(text) for device in device_list)
    )


@mcp.tool()
async def send_keys_text(text: str, value: str, contains: bool = False) -> typing.Any:
    """按 text 定位并点击第一个控件，然后输入给定内容。"""
    logger.info(f"Send keys by text {text} value={value} contains={contains}")
    return await asyncio.gather(
        *(device.send_keys_by_text(text, value, contains=contains) for device in device_list)
    )


@mcp.tool()
async def send_keys_resource_id(resource_id: str, value: str, contains: bool = False) -> typing.Any:
    """按 resource-id 定位并点击第一个控件，然后输入给定内容。"""
    logger.info(f"Send keys by resource-id {resource_id} value={value} contains={contains}")
    return await asyncio.gather(
        *(device.send_keys_by_resource_id(resource_id, value, contains=contains) for device in device_list)
    )


@mcp.tool()
async def send_keys_desc(content_desc: str, value: str, contains: bool = False) -> typing.Any:
    """按 content-desc 定位并点击第一个控件，然后输入给定内容。"""
    logger.info(f"Send keys by content-desc {content_desc} value={value} contains={contains}")
    return await asyncio.gather(
        *(device.send_keys_by_desc(content_desc, value, contains=contains) for device in device_list)
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
