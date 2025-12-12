from typing import TypedDict, Dict, List, Optional


class AgentState(TypedDict, total=False):
    raw_request: str
    fields: Dict[str, str]          # title, description, requirements, validation
    missing: List[str]
    card: Optional[str]
