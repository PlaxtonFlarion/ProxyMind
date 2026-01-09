import json
import httpx
import typing


async def stream_planner(
    payload: dict[str, typing.Any],
    on_event: typing.Callable,
    *,
    timeout: float = 60.0,
):

    url     = f"https://api.appserverx.com/planner"
    headers = {
        "Accept": "text/event-stream", "Content-Type": "applications/json"
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

                await on_event(event); yield event


if __name__ == '__main__':
    pass
