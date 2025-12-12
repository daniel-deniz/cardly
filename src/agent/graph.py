from langgraph.graph import StateGraph, END
from .state import AgentState
from . import nodes


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("init_state", nodes.init_state)
    g.add_node("choose_type_and_mode", nodes.choose_type_and_mode)
    g.add_node("check_missing", nodes.check_missing)
    g.add_node("ask_for_missing_one_by_one", nodes.ask_for_missing_one_by_one)
    g.add_node("ask_validation_if_needed", nodes.ask_validation_if_needed)
    g.add_node("build_card", nodes.build_card)

    g.set_entry_point("init_state")
    g.add_edge("init_state", "choose_type_and_mode")
    g.add_edge("choose_type_and_mode", "check_missing")

    def route_missing(state: AgentState) -> str:
        missing = state.get("missing") or []
        return "ask_for_missing_one_by_one" if len(missing) > 0 else "ask_validation_if_needed"

    g.add_conditional_edges("check_missing", route_missing, {
        "ask_for_missing_one_by_one": "ask_for_missing_one_by_one",
        "ask_validation_if_needed": "ask_validation_if_needed",
    })

    g.add_edge("ask_for_missing_one_by_one", "check_missing")
    g.add_edge("ask_validation_if_needed", "build_card")
    g.add_edge("build_card", END)

    return g.compile()
