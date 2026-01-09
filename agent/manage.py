#  __  __
# |  \/  | __ _ _ __   __ _  __ _  ___
# | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \
# | |  | | (_| | | | | (_| | (_| |  __/
# |_|  |_|\__,_|_| |_|\__,_|\__, |\___|
#                           |___/
#

import typing
import asyncio
from agent.device import Device
from agent.terminal import Terminal
from utils import const


class McpServer(object):

    def __init__(self, program: str):
        self.program = program
        self.transports: typing.Optional[asyncio.subprocess.Process] = None

    async def input_stream(self) -> None:
        async for line in self.transports.stdout:
            print(line.decode(const.CHARSET).strip())

    async def error_stream(self) -> None:
        async for line in self.transports.stderr:
            print(line.decode(const.CHARSET).strip())

    async def mcp_begin(self) -> None:
        if self.transports and self.transports.returncode is None:
            return None

        cmd = [self.program]
        self.transports = await Terminal.cmd_link(cmd)

        asyncio.create_task(self.input_stream())
        asyncio.create_task(self.error_stream())

        await asyncio.sleep(1)

        print("✅ MCP started")

    async def mcp_final(self) -> None:
        if not self.transports or self.transports.returncode is not None:
            return None

        print("🛑 Stopping MCP...")

        self.transports.terminate()
        try:
            await asyncio.wait_for(self.transports.wait(), timeout=5)
        except asyncio.TimeoutError:
            self.transports.kill()

        print("✅ MCP stopped")


class Manage(object):

    def __init__(self, adb: str) -> None:
        self.adb = adb

    async def devices(self) -> list[Device]:
        cmd = [self.adb, "devices"]
        resp = await Terminal.cmd_line(cmd)
        return []


if __name__ == '__main__':
    pass
