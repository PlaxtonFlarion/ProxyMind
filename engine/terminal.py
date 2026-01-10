#  _____                   _             _
# |_   _|__ _ __ _ __ ___ (_)_ __   __ _| |
#   | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | |
#   | |  __/ |  | | | | | | | | | | (_| | |
#   |_|\___|_|  |_| |_| |_|_|_| |_|\__,_|_|
#

import typing
import asyncio
from utils import const


class Terminal(object):

    @staticmethod
    async def cmd_line(cmd: list[str]) -> typing.Any:
        transports = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await transports.communicate()

        if stdout:
            return stdout.decode(const.CHARSET, const.IGNORE).strip()
        if stderr:
            return stderr.decode(const.CHARSET, const.IGNORE).strip()

    @staticmethod
    async def cmd_link(cmd: list[str]) -> asyncio.subprocess.Process:
        transports = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        return transports


if __name__ == '__main__':
    pass
