import asyncio
import logging
import click
import uvicorn
import json

from mcp.types import Tool as MCPTool
from mcp.types import TextContent
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route

from xga_agent_tool.tool_base import XGAAgentResult
from xga_agent_tool.a2a.helper import invoke_agent,get_a2a_tools_info
from xga_agent_tool.a2a.config import load_a2a_config
from xga_agent_tool.utils.setup_env import setup_env_logging

async def create_a2a_mcp_server()-> Server:
    a2a_tools_config = load_a2a_config()
    a2a_tools_info = await get_a2a_tools_info(a2a_tools_config)

    app = Server("XGA A2A Agent Tool Proxy Server")

    @app.list_tools()
    async def list_tools() -> list[MCPTool]:
        nonlocal a2a_tools_info
        # refresh agent tool, agent may be start after proxy
        a2a_tools_info = await get_a2a_tools_info(a2a_tools_config)
        tool_schemas: list[MCPTool] = []
        agent_tool_names = []
        for tool_name in a2a_tools_info:
            tool_info = a2a_tools_info[tool_name]
            tool_schemas.append(tool_info.mcp_tool_schema)
            agent_tool_names.append(tool_name)
        logging.info(f"--- MCP list_tools: Total {len(tool_schemas)} tools, tools: {agent_tool_names}")
        return tool_schemas


    @app.call_tool()
    async def call_tool(name: str, arguments: dict)-> list[TextContent]:
        logging.info(f"--- MCP call_tool: tool_name={name}, args={arguments}")
        try:
            tool_info = a2a_tools_info[name]
            task_id = arguments["task_id"]
            input = arguments['input']
            agent_card = tool_info.agent_card
            result = await invoke_agent(task_id, input, agent_card)
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logging.error(f"MCP call_tool: Call tool '{name}' error: {e}")
            error = XGAAgentResult(type="error", content=f"Call tool unexpect error: {e}")
            return  [TextContent(type="text", text=json.dumps(error))]

    return app


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to listen on for SSE")
@click.option("--port", default=21010, help="Port to listen on for SSE")
def main(host: str, port: int):
    setup_env_logging()

    app = asyncio.run(create_a2a_mcp_server())

    sse = SseServerTransport("/messages/")
    async def handle_sse(request):
        async with sse.connect_sse(
                request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )
        return Response()

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    logging.info(f"****** XGA A2A Agent Tool Proxy start on host={host}, port={port} ******")
    uvicorn.run(starlette_app, host=host, port=port)

if __name__ == "__main__":
    main()
