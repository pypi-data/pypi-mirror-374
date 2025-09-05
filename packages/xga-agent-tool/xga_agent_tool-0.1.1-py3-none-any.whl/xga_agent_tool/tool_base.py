from typing import Optional, List, Literal, TypedDict

class XGAError(Exception):
    """Custom exception for errors in the XGA system."""
    pass

class XGAAgentResult(TypedDict, total=False):
    type: Literal["ask", "answer", "error"]
    content: str
    attachments: Optional[List[str]]