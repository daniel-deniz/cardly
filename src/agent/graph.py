from langgraph.graph import StateGraph, END
from .state import AgentState
from . import nodes


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("init_state", nodes.init_state)
    g.add_node("llm_fill_from_request", nodes.llm_fill_from_request)
    g.add_node("llm_edit_from_instruction", nodes.llm_edit_from_instruction)
    g.add_node("check_missing", nodes.check_missing)
    g.add_node("ask_for_missing_one_by_one", nodes.ask_for_missing_one_by_one)
    g.add_node("build_card", nodes.build_card)

    g.set_entry_point("init_state")

    def route_create_or_edit(state: AgentState) -> str:
        raw = (state.get("raw_request") or "").lower()
        fields = state.get("fields") or {}
        has_existing = bool(fields.get("title") or fields.get("requirements"))

        # Si el usuario pide explícitamente una tarjeta nueva => CREATE
        new_signals = ["otra tarjeta", "nueva tarjeta", "crea otra", "crea una tarjeta", "crear tarjeta", "dame otra tarjeta"]
        if any(s in raw for s in new_signals):
            return "llm_fill_from_request"

        # Si hay tarjeta previa y el usuario pide cambios => EDIT
        edit_signals = [
            "simplifica", "resumen", "más breve", "mas breve", "quita", "elimina",
            "añade", "agrega", "cambia", "reescribe", "mejora", "formato",
            "sin validación", "sin validacion"
        ]
        if has_existing and any(s in raw for s in edit_signals):
            return "llm_edit_from_instruction"

        # Por defecto: crear
        return "llm_fill_from_request"

    g.add_conditional_edges(
        "init_state",
        route_create_or_edit,
        {
            "llm_fill_from_request": "llm_fill_from_request",
            "llm_edit_from_instruction": "llm_edit_from_instruction",
        },
    )

    # CREATE flow
    g.add_edge("llm_fill_from_request", "check_missing")

    def route_missing(state: AgentState) -> str:
        missing = state.get("missing") or []
        return "ask_for_missing_one_by_one" if len(missing) > 0 else "build_card"

    g.add_conditional_edges(
        "check_missing",
        route_missing,
        {
            "ask_for_missing_one_by_one": "ask_for_missing_one_by_one",
            "build_card": "build_card",
        },
    )

    g.add_edge("ask_for_missing_one_by_one", "check_missing")

    # EDIT flow
    g.add_edge("llm_edit_from_instruction", "build_card")

    g.add_edge("build_card", END)

    return g.compile()
