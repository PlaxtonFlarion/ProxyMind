import typing
from agent.terminal import Terminal


class Device(object):

    def __init__(self, adb: str, serial: str) -> None:
        self.prefix = [adb, "-s", serial]

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


if __name__ == '__main__':
    pass
