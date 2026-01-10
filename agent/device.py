import re
import typing
import xml.etree.ElementTree as Et
from agent.terminal import Terminal


class Device(object):
    """基于 ADB 的设备操作封装。"""

    def __init__(self, adb: str, serial: str) -> None:
        """初始化设备前缀命令。"""
        self.prefix = [adb, "-s", serial]

    @staticmethod
    def _node_center(bounds: str) -> tuple[int, int] | None:
        """计算 bounds 的中心点坐标。"""
        if not (match := re.match(r"\[(\d+),(\d+)]\[(\d+),(\d+)]", bounds)):
            return None
        x1, y1, x2, y2 = map(int, match.groups())

        return (x1 + x2) // 2, (y1 + y2) // 2

    @staticmethod
    def _match_attr(value: str | None, target: str, contains: bool) -> bool:
        """根据匹配模式判断属性是否命中。"""
        if value is None: return False

        return target in value if contains else value == target

    async def dump_ui_xml(self) -> str | None:
        """生成并读取 UI 层级 XML。"""
        cmd = self.prefix + [
            "shell", "uiautomator", "dump", "/sdcard/window_dump.xml"
        ]
        await Terminal.cmd_line(cmd)

        cmd = self.prefix + [
            "shell", "cat", "/sdcard/window_dump.xml"
        ]
        return await Terminal.cmd_line(cmd)

    async def _find_first_node(
        self,
        *,
        text: str | None = None,
        resource_id: str | None = None,
        content_desc: str | None = None,
        contains: bool = False,
    ) -> Et.Element | None:
        """从 XML 中按条件查找第一个匹配节点。"""

        if not (xml_text := await self.dump_ui_xml()):
            return None

        for node in Et.fromstring(xml_text).iter("node"):
            if text and self._match_attr(node.get("text"), text, contains):
                return node
            if resource_id and self._match_attr(node.get("resource-id"), resource_id, contains):
                return node
            if content_desc and self._match_attr(node.get("content-desc"), content_desc, contains):
                return node

        return None

    async def click_by_text(self, text: str, *, contains: bool = False) -> typing.Any:
        """按 text 定位并点击第一个匹配控件。"""
        if not (node := await self._find_first_node(text=text, contains=contains)):
            return None
        if not (center := self._node_center(node.get("bounds", ""))):
            return None

        return await self.tap(center[0], center[1])

    async def click_by_resource_id(self, resource_id: str, *, contains: bool = False) -> typing.Any:
        """按 resource-id 定位并点击第一个匹配控件。"""
        if not (node := await self._find_first_node(resource_id=resource_id, contains=contains)):
            return None
        if not (center := self._node_center(node.get("bounds", ""))):
            return None

        return await self.tap(center[0], center[1])

    async def click_by_desc(self, content_desc: str, *, contains: bool = False) -> typing.Any:
        """按 content-desc 定位并点击第一个匹配控件。"""
        if not (node := await self._find_first_node(content_desc=content_desc, contains=contains)):
            return None
        if not (center := self._node_center(node.get("bounds", ""))):
            return None

        return await self.tap(center[0], center[1])

    async def send_keys(self, text: str) -> typing.Any:
        """向当前焦点输入框输入文本。"""
        cmd = self.prefix + [
            "shell", "input", "text", text
        ]
        return await Terminal.cmd_line(cmd)

    async def tap(self, x: int, y: int) -> typing.Any:
        """点击绝对坐标。"""
        cmd = self.prefix + [
            "shell", "input", "tap", str(x), str(y)
        ]
        return await Terminal.cmd_line(cmd)

    async def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> typing.Any:
        """滑动操作。"""
        cmd = self.prefix + [
            "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)
        ]
        return await Terminal.cmd_line(cmd)

    async def key_event(self, keycode: int) -> typing.Any:
        """发送 Android keyevent。"""
        cmd = self.prefix + [
            "shell", "input", "keyevent", str(keycode)
        ]
        return await Terminal.cmd_line(cmd)


if __name__ == '__main__':
    pass
