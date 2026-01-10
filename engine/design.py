#  ____            _
# |  _ \  ___  ___(_) __ _ _ __
# | | | |/ _ \/ __| |/ _` | '_ \
# | |_| |  __/\__ \ | (_| | | | |
# |____/ \___||___/_|\__, |_| |_|
#                    |___/
#

import typing
from rich.console import Console
from utils import const


class Design(object):

    console: typing.Optional["Console"] = Console()

    def __init__(self, design_level: str = const.SHOW_LEVEL):
        self.design_level = design_level

    class Doc(object):

        @classmethod
        def log(cls, text: typing.Any) -> None:
            Design.console.print(const.PRINT_HEAD, f"[bold]{text}")

        @classmethod
        def suc(cls, text: typing.Any) -> None:
            Design.console.print(const.PRINT_HEAD, f"{const.SUC}{text}")

        @classmethod
        def wrn(cls, text: typing.Any) -> None:
            Design.console.print(const.PRINT_HEAD, f"{const.WRN}{text}")

        @classmethod
        def err(cls, text: typing.Any) -> None:
            Design.console.print(const.PRINT_HEAD, f"{const.ERR}{text}")


if __name__ == '__main__':
    pass
