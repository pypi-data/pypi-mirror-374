from dataclasses import dataclass
from typing import TypedDict

from a2a.types import AgentCard
from mcp.types import Tool as MCPTool

class A2AToolConfig(TypedDict, total=False):
    agent_card_base_url: str
    agent_card_path: str
    tool_name: str
    tool_desc: str
    input_desc: str

@dataclass
class A2AToolInfo:
    tool_name: str
    agent_card: AgentCard
    mcp_tool_schema: MCPTool
