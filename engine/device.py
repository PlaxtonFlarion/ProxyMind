#  ____             _
# |  _ \  _____   _(_) ___ ___
# | | | |/ _ \ \ / / |/ __/ _ \
# | |_| |  __/\ V /| | (_|  __/
# |____/ \___| \_/ |_|\___\___|
#

import re
import time
import typing
import asyncio
import xml.etree.ElementTree as Et
from pathlib import Path
from engine.terminal import Terminal
from utils import const


class Device(object):

    def __init__(self, adb: str, serial: str) -> None:
        self.prefix = [adb, "-s", serial]

    async def dump_ui_xml(self) -> str | None:
        xml_file = "/data/local/tmp/window_dump.xml"

        cmd = self.prefix + [
            "shell", "uiautomator", "dump", "--compressed", xml_file
        ]
        await Terminal.cmd_line(cmd)

        await asyncio.sleep(1)

        cmd = self.prefix + [
            "shell", "cat", xml_file
        ]
        for _ in range(5):
            xml = await Terminal.cmd_line(cmd)

            if isinstance(xml, bytes):
                xml = xml.decode(const.CHARSET, const.IGNORE)
            if xml and "<hierarchy" in xml:
                return xml
            await asyncio.sleep(0.2)

        return None

    async def click(self, by: typing.Literal["text", "resource-id"], value: str) -> typing.Any:
        if not (xml := await self.dump_ui_xml()):
            return None

        node = None
        for n in Et.fromstring(xml).iter("node"):
            if n.attrib.get(by) == value:
                node = n.attrib; break

        if not node or not (bounds := node.get("bounds")):
            return None

        match = re.match(r"\[(\d+),(\d+)]\[(\d+),(\d+)]", bounds)
        x1, y1, x2, y2 = map(int, match.groups())

        center = (x1 + x2) // 2, (y1 + y2) // 2

        return await self.tap(center[0], center[1])

    async def send_keys(self, text: str) -> typing.Any:
        cmd = self.prefix + [
            "shell", "input", "text", text
        ]
        return await Terminal.cmd_line(cmd)

    async def tap(self, x: int, y: int) -> typing.Any:
        cmd = self.prefix + [
            "shell", "input", "tap", str(x), str(y)
        ]
        return await Terminal.cmd_line(cmd)

    async def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> typing.Any:
        cmd = self.prefix + [
            "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)
        ]
        return await Terminal.cmd_line(cmd)

    async def key_event(self, keycode: int) -> typing.Any:
        cmd = self.prefix + [
            "shell", "input", "keyevent", str(keycode)
        ]
        return await Terminal.cmd_line(cmd)

    async def screenshot(self, out_dir: str = ".") -> str:
        (out := Path(out_dir)).mkdir(parents=True, exist_ok=True)

        filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
        remote   = f"/sdcard/{filename}"
        local    = out / filename

        cmd = self.prefix + ["shell", "screencap", "-p", remote]
        await Terminal.cmd_line(cmd)

        cmd = self.prefix + ["pull", remote, str(local)]
        await Terminal.cmd_line(cmd)

        cmd = self.prefix + ["shell", "rm", "-f", remote]
        await Terminal.cmd_line(cmd)

        return str(local)


if __name__ == '__main__':
    pass
