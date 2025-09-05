import httpx
import logging

from typing import Any, List, Optional
from uuid import uuid4

from mcp.types import Tool as MCPTool

from xga_agent_tool.tool_base import XGAAgentResult
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import AgentCard,Task, MessageSendParams,SendMessageRequest

from xga_agent_tool.a2a.base import A2AToolInfo, A2AToolConfig

async def get_a2a_tools_info(tools_config: List[A2AToolConfig]) -> dict[str, A2AToolInfo]:
    a2a_tools_info: dict[str, A2AToolInfo] = {}

    for tool_config in tools_config:
        try:
            card_base_url = tool_config.get('agent_card_base_url', None)
            tool_name = tool_config.get('tool_name', None)
            if tool_name is None or card_base_url is None:
                logging.error(f"*** get_a2a_tools_info: tool_name and agent_card_base_url are required in config file")
                continue

            card_path = tool_config.get('agent_card_path', None)
            agent_card = await get_agent_card(card_base_url, card_path)
            if agent_card is None:
                continue

            mcp_tool_schema = generate_mcp_tool_schema(tool_config, agent_card)
            agent_info = A2AToolInfo(
                tool_name       = tool_name,
                agent_card      = agent_card,
                mcp_tool_schema = mcp_tool_schema
            )

            a2a_tools_info[tool_name] = agent_info
        except Exception as e:
            logging.error(f"get_a2a_tools_info: Unexpected error: {e}")

    return a2a_tools_info

def generate_mcp_tool_schema(tool_config: A2AToolConfig, agent_card: AgentCard) -> MCPTool:
    tool_name = tool_config['tool_name']
    tool_desc = tool_config.get('tool_desc', None) or agent_card.description
    input_desc = tool_config.get('input_desc', '')
    mcp_tool_schema = MCPTool(
        name = tool_name,
        description = tool_desc,
        inputSchema = {
            "type": "object",
            "required": ["input"],
            "properties": {
                "input": {
                    "type": "string",
                    "description": input_desc,
                }
            }
        }
    )
    return mcp_tool_schema


async def get_agent_card(base_url: str, agent_card_path: Optional[str]=None) -> AgentCard:
    agent_card_path = agent_card_path or '/.well-known/agent.json'
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client, base_url, agent_card_path)

        final_agent_card_to_use: AgentCard = None
        try:
            logging.info(f"get_agent_card: Fetch public agent card from '{base_url}{agent_card_path}'")
            _public_card = await resolver.get_agent_card()
            logging.info(f"=== Agent card '{_public_card.name} Fetched")
            final_agent_card_to_use = _public_card
        except Exception as e:
            logging.error(f"get_agent_card : Fetch public agent card from '{base_url}{agent_card_path}', error: {e}")

        return final_agent_card_to_use


async def invoke_agent(task_id: str, input: str, agent_card: AgentCard) -> XGAAgentResult:
    async with httpx.AsyncClient() as httpx_client:
        agent_name = agent_card.name
        a2a_client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
        logging.info(f'invoke_agent: A2AClient[agent_name={agent_name}, url={agent_card.url}] initialized .')

        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {
                        'kind': 'text',
                        'text': input
                    }
                ],
                'messageId': uuid4().hex,
            },
        }
        return await _send_message_by_rest(task_id, send_message_payload, a2a_client, agent_name)


async def _send_message_by_rest(task_id: str, payload: dict[str, Any], a2a_client: A2AClient, agent_name: str) -> XGAAgentResult:
    try:
        result: XGAAgentResult = XGAAgentResult(type="error", content='unknown error')
        request = SendMessageRequest(id=task_id, params=MessageSendParams(**payload))
        event = await a2a_client.send_message(request)
        if hasattr(event.root, 'error') and event.root.error:
            error = f"Invoke agent '{agent_name}' failed, error: {event.root.error.message}"
            logging.error(f"--- A2A_RESULT[{agent_name}]: type=error, error: {error}")
            result = XGAAgentResult(type="error", content=error)
            return result

        a2a_result = event.root.result

        if isinstance(a2a_result, Task):
            task = a2a_result
            state = task.status.state if task.status and hasattr(task.status, 'state') else "empty"
            if task.artifacts and len(task.artifacts) > 0:
                content = task.artifacts[0].parts[0].root.text
                result = XGAAgentResult(type="answer", content=content)
                logging.info(f"--- A2A_RESULT[{agent_name}]:  type=answer, artifact: '{content}'")
            elif state == "input-required":
                input_message = None
                if task.status.message and hasattr(task.status.message, 'parts'):
                    for part in task.status.message.parts:
                        root_part = part.root
                        if hasattr(root_part, 'text'):
                            input_message = root_part.text
                            break
                if input_message:
                    logging.info(f"--- A2A_RESULT[{agent_name}]: type=ask, input-required: '{input_message}'")
                    result = XGAAgentResult(type="ask", content=input_message)
                else:
                    error = f"Invoke agent '{agent_name}' error: 'input-required' status message has no 'text' part"
                    logging.error(f"--- A2A_RESULT[{agent_name}]: type=error, error: {error}")
                    result = XGAAgentResult(type="error", content=error)
            else:
                error = f"Invoke agent '{agent_name}' error: unexpect task status state '{state}'"
                logging.error(f"A2A_RESULT[{agent_name}]: type=error, error: {error}")
                result = XGAAgentResult(type="error", content=error)
        else:
            error = f"Invoke agent '{agent_name}' error: unexpect class type '{type(a2a_result).__name__}'"
            logging.error(f"A2A_RESULT[{agent_name}]: type=error, error: {error}")
            result = XGAAgentResult(type="error", content=error)

        return result
    except Exception as e:
        error = f"Invoke agent '{agent_name}', send_message error: {e}"
        logging.error(f"A2A_RESULT[{agent_name}]: type=error, error: {error}")
        return XGAAgentResult(type="error", content=error)

if __name__ == "__main__":
    import asyncio
    from xga_agent_tool.utils.setup_env import setup_logging

    async def main():
        agent_card = await get_agent_card("http://localhost:37070")

        result = await invoke_agent("task1", "F02 Fault", agent_card)
        print(result)

        result = await invoke_agent("task2", "Error Fault", agent_card)
        print(result)

    setup_logging()
    asyncio.run(main())