#   ____            __ _
#  / ___|_ __ __ _ / _| |_
# | |   | '__/ _` | |_| __|
# | |___| | | (_| |  _| |_
#  \____|_|  \__,_|_|  \__|
#

import sys
from loguru import logger
from utils import const


async def setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr, level=const.LOG_LEVEL, format=const.LOG_FORMAT
    )


if __name__ == '__main__':
    pass
