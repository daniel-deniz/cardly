from typing import TypedDict, Dict, List, Optional, Literal


TicketType = Literal["funcionalidad", "bug"]
OutputMode = Literal["completa", "simplificada"]


class AgentState(TypedDict, total=False):
    raw_request: str
    ticket_type: TicketType
    output_mode: OutputMode

    fields: Dict[str, str]          # title, description, requirements, validation
    missing: List[str]
    card: Optional[str]
    