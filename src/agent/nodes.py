from typing import Dict, List
from .state import AgentState
from .llm import generate_ticket_structured, edit_ticket_structured

REQUIRED_FIELDS = ["title", "description", "requirements"]


def _detect_type_from_text(raw_lower: str) -> str | None:
    bug_signals = [
        "bug", "error", "falla", "no funciona", "se cuelga", "se queda colgado",
        "crash", "rompe", "incorrecto", "no carga", "bloquea", "no deja",
        "no responde", "congelado", "se congela", "timeout", "timeouts", "lento", "lentitud"
    ]
    feat_signals = ["funcionalidad", "feature", "se requiere", "añadir", "implementar", "crear"]

    if any(s in raw_lower for s in bug_signals):
        return "bug"
    if any(s in raw_lower for s in feat_signals):
        return "funcionalidad"
    return None


def _human_type(ticket_type: str) -> str:
    t = (ticket_type or "").lower().strip()
    return "Bug" if t == "bug" else "Funcionalidad"


def _user_requested_no_validation(raw_lower: str) -> bool:
    return any(
        s in raw_lower
        for s in [
            "sin validación", "sin validacion",
            "no requiere validación", "no requiere validacion",
            "sin validar", "sin pruebas",
            "quita la validación", "quita la validacion",
            "elimina la validación", "elimina la validacion",
        ]
    )


def _fallback_validation(ticket_type: str, raw_request: str) -> List[str]:
    """Validación mínima y verificable si el LLM no devuelve nada."""
    t = (ticket_type or "funcionalidad").lower().strip()
    raw_lower = (raw_request or "").lower()

    if t == "bug":
        checks = [
            "Reproducir el problema con el mismo escenario indicado y confirmar el fallo actual.",
            "Aplicar la corrección y verificar que el resultado esperado se cumple (sin el error).",
            "Repetir el escenario en distintos usuarios/perfiles si aplica y confirmar consistencia.",
        ]
        if any(k in raw_lower for k in ["lento", "lentitud", "bloquea", "cuelga", "congela", "timeout", "timeouts", "query", "queries"]):
            checks.append("Confirmar que no hay bloqueo y que el tiempo de respuesta es razonable bajo carga.")
        return checks[:4]

    # funcionalidad
    checks = [
        "Verificar que la funcionalidad aparece y se comporta como se espera en el módulo indicado.",
        "Comprobar el comportamiento con usuarios con y sin permisos (si aplica).",
        "Validar edge cases básicos: estado vacío / error de carga / sin datos, sin romper el flujo.",
    ]
    return checks[:4]


def init_state(state: AgentState) -> AgentState:
    fields = state.get("fields") or {}
    fields.setdefault("title", "")
    fields.setdefault("description", state.get("raw_request", "").strip())
    fields.setdefault("requirements", "")
    fields.setdefault("validation", "")

    ticket_type = state.get("ticket_type") or "funcionalidad"
    output_mode = state.get("output_mode") or "completa"

    return {"fields": fields, "ticket_type": ticket_type, "output_mode": output_mode}


def llm_fill_from_request(state: AgentState) -> AgentState:
    raw = state.get("raw_request", "").strip()
    raw_lower = raw.lower()

    no_validation_requested = _user_requested_no_validation(raw_lower)

    text_type = _detect_type_from_text(raw_lower)
    data = generate_ticket_structured(raw)

    llm_type = (data.get("ticket_type") or "").lower().strip() or "funcionalidad"
    ticket_type = text_type if text_type else llm_type
    output_mode = data.get("output_mode", "completa")

    requirements = data.get("requirements") or []
    validation = data.get("validation") or []

    # ✅ Guardrail: si NO pidieron "sin validación" y viene vacía → fallback
    if (not no_validation_requested) and (len([v for v in validation if str(v).strip()]) == 0):
        validation = _fallback_validation(ticket_type, raw)

    if no_validation_requested:
        validation = []

    fields = {
        "title": (data.get("title") or "").strip(),
        "description": (data.get("description") or "").strip(),
        "requirements": "\n".join([f"- {r.strip()}" for r in requirements if str(r).strip()]),
        "validation": "\n".join([f"- {v.strip()}" for v in validation if str(v).strip()]),
    }

    return {
        "ticket_type": ticket_type,
        "output_mode": output_mode,
        "fields": fields,
    }


def llm_edit_from_instruction(state: AgentState) -> AgentState:
    raw = state.get("raw_request", "").strip()
    raw_lower = raw.lower()

    no_validation_requested = _user_requested_no_validation(raw_lower)

    current_fields = state.get("fields") or {}
    data = edit_ticket_structured(current_fields, raw)

    text_type = _detect_type_from_text(raw_lower)
    llm_type = (data.get("ticket_type") or state.get("ticket_type") or "funcionalidad").lower().strip()
    ticket_type = text_type if text_type else llm_type

    output_mode = data.get("output_mode", state.get("output_mode", "completa"))

    requirements = data.get("requirements") or []
    validation = data.get("validation") or []

    # ✅ Guardrail también en EDIT
    if (not no_validation_requested) and (len([v for v in validation if str(v).strip()]) == 0):
        validation = _fallback_validation(ticket_type, raw)

    if no_validation_requested:
        validation = []

    fields = {
        "title": (data.get("title") or current_fields.get("title") or "").strip(),
        "description": (data.get("description") or current_fields.get("description") or "").strip(),
        "requirements": "\n".join([f"- {r.strip()}" for r in requirements if str(r).strip()]) or current_fields.get("requirements", ""),
        "validation": "\n".join([f"- {v.strip()}" for v in validation if str(v).strip()]),
    }

    return {
        "ticket_type": ticket_type,
        "output_mode": output_mode,
        "fields": fields,
    }


def check_missing(state: AgentState) -> AgentState:
    fields = state.get("fields") or {}
    missing: List[str] = [k for k in REQUIRED_FIELDS if not fields.get(k, "").strip()]
    return {"missing": missing}


def ask_for_missing_one_by_one(state: AgentState) -> AgentState:
    fields: Dict[str, str] = state.get("fields") or {}
    missing = state.get("missing") or []
    key = missing[0]

    prompts = {
        "title": "Título (muy breve, estilo: [Módulo] - [2-3 palabras]): ",
        "description": "Descripción (qué se quiere lograr o solucionar, 1-3 frases): ",
        "requirements": "Requisitos (bullets; escribe varios separados por ';' ): ",
    }

    value = input(prompts.get(key, f"{key}: ")).strip()

    if key == "requirements":
        items = [x.strip() for x in value.split(";") if x.strip()]
        value = "\n".join([f"- {i}" for i in items]) if items else ""

    fields[key] = value
    return {"fields": fields}


def build_card(state: AgentState) -> AgentState:
    f = state.get("fields") or {}
    output_mode = state.get("output_mode", "completa")
    ticket_type = state.get("ticket_type", "funcionalidad")

    title = f.get("title", "").strip()
    desc = f.get("description", "").strip()
    req = f.get("requirements", "").strip()
    val = f.get("validation", "").strip()

    tipo_humano = _human_type(ticket_type)

    if output_mode == "simplificada":
        card = (
            f"**Tipo:** {tipo_humano}\n"
            f"---\n"
            f"**Título:** {title}\n\n"
            f"**Requisitos:**\n{req}\n\n"
            f"**Validación:** No requerida.\n"
        )
        return {"card": card}

    card = (
        f"**Tipo:** {tipo_humano}\n"
        f"---\n"
        f"**Título:** {title}\n\n"
        f"**Descripción:**\n{desc}\n\n"
        f"**Requisitos:**\n{req}\n"
    )

    if val:
        card += f"\n**Validación:**\n{val}\n"
    else:
        card += "\n**Validación:** No requerida.\n"

    return {"card": card}
