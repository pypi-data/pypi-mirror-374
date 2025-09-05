import os
import yaml

from typing import  Dict, List
from xga_agent_tool.tool_base import XGAError
from xga_agent_tool.a2a.base import A2AToolConfig

def load_a2a_config() -> List[A2AToolConfig]:
    file_path = os.getenv('XGA_A2A_CONFIG_FILE', "a2a_config.yaml")
    if not os.path.exists(file_path):
        raise XGAError(f"A2A Config yaml file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
        if config is None:
            raise XGAError("A2A Config yaml file is empty or invalid.")
        return config.values()
    except Exception as e:
        raise XGAError(f"Failed to load A2A Config yaml file from {file_path}: {e}")