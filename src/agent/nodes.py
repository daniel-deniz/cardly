from typing import Dict, List
from .state import AgentState

REQUIRED_FIELDS = ["title", "description", "requirements", "validation"]


def init_state(state: AgentState) -> AgentState:
    fields = state.get("fields") or {}
    # Aseguramos que existen las claves aunque estén vacías
    for k in REQUIRED_FIELDS:
        fields.setdefault(k, "")
    return {"fields": fields}


def check_missing(state: AgentState) -> AgentState:
    fields = state.get("fields") or {}
    missing: List[str] = [k for k in REQUIRED_FIELDS if not fields.get(k, "").strip()]
    return {"missing": missing}


def ask_for_missing(state: AgentState) -> AgentState:
    fields: Dict[str, str] = state.get("fields") or {}
    missing = state.get("missing") or []

    print("\nFalta información para generar la tarjeta.")
    for key in missing:
        label = {
            "title": "Título",
            "description": "Descripción",
            "requirements": "Requisitos",
            "validation": "Validación",
        }.get(key, key)

        value = input(f"- {label}: ").strip()
        fields[key] = value

    return {"fields": fields}


def build_card(state: AgentState) -> AgentState:
    f = state.get("fields") or {}

    card = (
        f"**Título:** {f.get('title','').strip()}\n\n"
        f"**Descripción:**\n{f.get('description','').strip()}\n\n"
        f"**Requisitos:**\n{f.get('requirements','').strip()}\n\n"
        f"**Validación:**\n{f.get('validation','').strip()}\n"
    )
    return {"card": card}
