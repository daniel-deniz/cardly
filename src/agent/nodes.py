from typing import Dict, List
from .state import AgentState

# Contrato del proyecto (tu prompt convertido en reglas simples)
REQUIRED_FIELDS = ["title", "description", "requirements"]  # validación solo si aplica


def init_state(state: AgentState) -> AgentState:
    fields = state.get("fields") or {}
    fields.setdefault("title", "")
    fields.setdefault("description", state.get("raw_request", "").strip())
    fields.setdefault("requirements", "")
    fields.setdefault("validation", "")  # opcional

    # defaults
    ticket_type = state.get("ticket_type") or "funcionalidad"
    output_mode = state.get("output_mode") or "completa"

    return {"fields": fields, "ticket_type": ticket_type, "output_mode": output_mode}


def choose_type_and_mode(state: AgentState) -> AgentState:
    print("\nTipo de tarjeta:")
    print("1) Funcionalidad (algo que hay que implementar)")
    print("2) Bug / Corrección (algo que no funciona)")

    choice = input("Elige 1 o 2 (por defecto 1): ").strip()
    ticket_type = "bug" if choice == "2" else "funcionalidad"

    print("\nFormato de salida:")
    print("1) Completa (con descripción + requisitos + validación si aplica)")
    print("2) Simplificada (más breve)")

    mode_choice = input("Elige 1 o 2 (por defecto 1): ").strip()
    output_mode = "simplificada" if mode_choice == "2" else "completa"

    return {"ticket_type": ticket_type, "output_mode": output_mode}


def check_missing(state: AgentState) -> AgentState:
    fields = state.get("fields") or {}
    missing: List[str] = [k for k in REQUIRED_FIELDS if not fields.get(k, "").strip()]
    return {"missing": missing}


def ask_for_missing_one_by_one(state: AgentState) -> AgentState:
    fields: Dict[str, str] = state.get("fields") or {}
    missing = state.get("missing") or []

    # preguntamos de una en una (menos abrumador)
    key = missing[0]

    prompts = {
        "title": (
            "Título (muy breve, estilo: [Módulo] - [2-3 palabras]): "
        ),
        "description": (
            "Descripción (qué se quiere lograr o solucionar, 1-3 frases): "
        ),
        "requirements": (
            "Requisitos (bullets; escribe varios separados por ';' ): "
        ),
    }

    value = input(prompts.get(key, f"{key}: ")).strip()

    # Normalizamos requisitos a bullets con •
    if key == "requirements":
        items = [x.strip() for x in value.split(";") if x.strip()]
        value = "\n".join([f"• {i}" for i in items]) if items else ""

    fields[key] = value
    return {"fields": fields}


def ask_validation_if_needed(state: AgentState) -> AgentState:
    # la validación es opcional, pero muy recomendable
    fields = state.get("fields") or {}
    current = fields.get("validation", "").strip()

    if current:
        return {}  # ya existe

    answer = input("\n¿Quieres añadir validación? (s/n, por defecto s): ").strip().lower()
    if answer in ("n", "no"):
        return {}

    val = input("Validación (bullets; separado por ';' ): ").strip()
    items = [x.strip() for x in val.split(";") if x.strip()]
    fields["validation"] = "\n".join([f"• {i}" for i in items]) if items else ""
    return {"fields": fields}


def build_card(state: AgentState) -> AgentState:
    f = state.get("fields") or {}
    ticket_type = state.get("ticket_type", "funcionalidad")
    output_mode = state.get("output_mode", "completa")

    # Prefijo de título opcional según tipo (sin emojis, estilo profesional)
    type_prefix = "BUG" if ticket_type == "bug" else "FEAT"

    title = f.get("title", "").strip()
    desc = f.get("description", "").strip()
    req = f.get("requirements", "").strip()
    val = f.get("validation", "").strip()

    if output_mode == "simplificada":
        card = (
            f"Título: [{type_prefix}] {title}\n"
            f"Requisitos:\n{req}\n"
        )
        return {"card": card}

    # completa
    card = (
        f"Título: [{type_prefix}] {title}\n\n"
        f"Descripción: {desc}\n\n"
        f"Requisitos:\n{req}\n"
    )

    if val:
        card += f"\nValidación:\n{val}\n"

    return {"card": card}
