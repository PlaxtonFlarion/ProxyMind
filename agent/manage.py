#  __  __
# |  \/  | __ _ _ __   __ _  __ _  ___
# | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \
# | |  | | (_| | | | | (_| | (_| |  __/
# |_|  |_|\__,_|_| |_|\__,_|\__, |\___|
#                           |___/
#

import typing
import asyncio
from pathlib import Path
from loguru import logger
from agent.device import Device
from agent.terminal import Terminal
from utils import const


class McpServer(object):

    def __init__(self, program: Path | str):
        self.program = str(program)
        self.transports: typing.Optional[asyncio.subprocess.Process] = None

    async def input_stream(self) -> None:
        async for line in self.transports.stdout:
            logger.info(line.decode(const.CHARSET, const.IGNORE).strip())

    async def error_stream(self) -> None:
        async for line in self.transports.stderr:
            logger.info(line.decode(const.CHARSET, const.IGNORE).strip())

    async def mcp_begin(self) -> None:
        if self.transports and self.transports.returncode is None:
            return None

        cmd = ["python", self.program]
        self.transports = await Terminal.cmd_link(cmd)

        asyncio.create_task(self.input_stream())
        asyncio.create_task(self.error_stream())

        await asyncio.sleep(1)

        logger.info("Ⓜ️ MCP started ...")

    async def mcp_final(self) -> None:
        if not self.transports or self.transports.returncode is not None:
            return None

        logger.info("☣️ MCP Stopping ...")

        self.transports.terminate()
        try:
            await asyncio.wait_for(self.transports.wait(), timeout=5)
        except asyncio.TimeoutError:
            self.transports.kill()

        logger.info("♻️ MCP stopped ...")


class Manage(object):

    def __init__(self, adb: str) -> None:
        self.adb = adb

    async def devices(self) -> list[Device]:
        cmd = [self.adb, "devices"]
        resp = await Terminal.cmd_line(cmd)

        if not resp or not (lines := [line.strip() for line in resp.splitlines() if line.strip()]):
            return []

        if "not found" in resp.lower() or resp.lower().startswith("adb:") or resp.lower().startswith("error"):
            return []

        devices: list[Device] = []
        for line in lines:
            if line.lower().startswith("list of devices"):
                continue

            if len(parts := line.split()) < 2:
                continue

            serial, status = parts[0], parts[1]
            if status != "device":
                continue

            devices.append(Device(self.adb, serial))

        return devices


if __name__ == '__main__':
    pass
