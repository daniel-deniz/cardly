from langgraph.graph import StateGraph, END
from .state import AgentState
from . import nodes


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("init_state", nodes.init_state)
    g.add_node("check_missing", nodes.check_missing)
    g.add_node("ask_for_missing", nodes.ask_for_missing)
    g.add_node("build_card", nodes.build_card)

    g.set_entry_point("init_state")
    g.add_edge("init_state", "check_missing")

    # Si faltan campos -> preguntar -> volver a comprobar
    def route(state: AgentState) -> str:
        missing = state.get("missing") or []
        return "ask_for_missing" if len(missing) > 0 else "build_card"

    g.add_conditional_edges("check_missing", route, {
        "ask_for_missing": "ask_for_missing",
        "build_card": "build_card",
    })

    g.add_edge("ask_for_missing", "check_missing")
    g.add_edge("build_card", END)

    return g.compile()
