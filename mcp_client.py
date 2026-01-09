import asyncio
from loguru import logger
from mcp import ClientSession, ListToolsResult
from mcp.client.streamable_http import streamable_http_client
from agent.manage import McpServer
from agent.terminal import Terminal
from utils import request


async def handle_event(event: dict) -> None:
    match event.get("type"):
        case "thinking": logger.info(
            f"🤔 PLAN {event['content']}"
        )
        # case "plan": logger.info(
        #     f"📋 PLAN RECEIVED {json.dumps(event['steps'], ensure_ascii=False, indent=2)}"
        # )
        case "done": logger.info(
            f"✅ PLAN DONE"
        )


async def main():
    # lsof -i :3333
    # lsof -ti :3333 | xargs kill -9
    # mcp run agent/mcp_server.py --transport=streamable-http

    program = "/Users/acekeppel/PycharmProjects/ProxyMind/applications/server.app/Contents/MacOS/server"
    await Terminal.cmd_line(["chmod", "+x", program])
    mcp_server = McpServer(program)
    await mcp_server.mcp_begin()

    try:
        async with streamable_http_client("http://127.0.0.1:3333/mcp") as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()

                list_tools: ListToolsResult = await session.list_tools()

                openai_tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description" : tool.description,
                            "parameters"  : tool.inputSchema
                        }
                    }
                    for tool in list_tools.tools
                ]

                for tool in openai_tools: logger.info(tool)

                async for plan in request.stream_planner(
                    payload={
                        "model"   : "llama-3.3-70b-versatile",
                        "message" : "打开登录页面，输入用户名 ace，输入密码 123456，然后点击登录按钮",
                        "tools"   : openai_tools,
                    },
                    on_event=handle_event
                ):

                    if plan.get("steps"):
                        for step in plan["steps"]:
                            action = step["action"]
                            print(f"\n>>> EXEC STEP {step['id']} {action}")
                            result = await session.call_tool(action["action"], action["args"])

                            if result.structuredContent:
                                print("Structured:", result.structuredContent)
                            elif result.content:
                                print("Text:", result.content[0].text)

                            await asyncio.sleep(1)

    except Exception as e:
        logger.error(e)

    finally:
        await mcp_server.mcp_final()


if __name__ == '__main__':
    asyncio.run(main())
