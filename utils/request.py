#  ____                            _
# |  _ \ ___  __ _ _   _  ___  ___| |_
# | |_) / _ \/ _` | | | |/ _ \/ __| __|
# |  _ <  __/ (_| | |_| |  __/\__ \ |_
# |_| \_\___|\__, |\__,_|\___||___/\__|
#               |_|
#

import json
import httpx
import typing
from loguru import logger


async def handle_event(event: dict) -> None:
    match event.get("type"):
        case "thinking":
            logger.info(f"🟣 Plan {event['content']}")
        case "plan":
            if steps := event.get("steps"):
                for step in steps: logger.info(f"🟠 Plan {step['action']}")
            else: logger.warning(f"🔴 Plan {event}")
        case "done":
            logger.info(f"🟢 Plan done ...")


async def stream_planner(payload: dict[str, typing.Any], timeout: float = 60.0) -> typing.AsyncGenerator[dict, None]:
    url     = f"https://api.appserverx.com/planner"
    headers = {
        "Accept": "text/event-stream", "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as resp:
            resp.raise_for_status()

            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue

                try:
                    event = json.loads(line[len("data:"):].strip())
                except json.JSONDecodeError:
                    continue

                await handle_event(event)

                yield event


if __name__ == '__main__':
    pass
