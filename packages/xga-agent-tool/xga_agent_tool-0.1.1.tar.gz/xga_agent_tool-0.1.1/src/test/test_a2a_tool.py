import asyncio
import click

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


@click.command()
@click.option("--host", default="localhost", help="Host to listen on for SSE")
@click.option("--port", default=21010, help="Port to listen on for SSE")
def main(host: str, port: int):
    url = f"http://{host}:{port}/sse"
    async def run_sse(url):
        async with sse_client(url, sse_read_timeout=5) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()

                # list available tools
                response = await session.list_tools()
                tools = response.tools
                print("\n list_tools:", [(tool.name, tool.description) for tool in tools])

                # call the tool
                task_id = "task_1"
                inputs = ["Fault code is F02", "Unknow Fault code"]
                for input in inputs:
                    result = await session.call_tool("query_equip_fault_cause", {'task_id': task_id, 'input': input})
                    print(f'\n call_tool: query_equip_fault_cause result={result}')

    asyncio.run(run_sse(url))


if __name__ == "__main__":
    main()
