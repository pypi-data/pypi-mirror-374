import click
import uvicorn
import logging

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from examples.a2a.simu_equip_fault_agent import get_agent_card, EquipFaultAgentExecutor
from xga_agent_tool.utils.setup_env import setup_logging

@click.command()
@click.option("--host", default="0.0.0.0", help="Host to listen on for SSE")
@click.option("--port", default=37070, help="Port to listen on for SSE")
def main(host: str, port: int):
    setup_logging()

    base_url = f"http://{host}:{port}/"

    public_agent_card = get_agent_card(base_url)

    request_handler = DefaultRequestHandler(
        agent_executor = EquipFaultAgentExecutor(),
        task_store = InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    logging.info(f"****** Example A2A Server start on host={host}, port={port} ******")
    uvicorn.run(server.build(), host=host, port=port)

if __name__ == '__main__':
    main()
