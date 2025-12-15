import streamlit as st
from agent.graph import build_graph

st.set_page_config(page_title="Draft", page_icon="🧰", layout="centered")

st.markdown(
    """
    <style>
      .block-container { max-width: 760px; padding-top: 2rem; }
      .stChatMessage { border-radius: 16px; }
      footer { visibility: hidden; }
      header { visibility: hidden; }

      /* Toolbar estilo "ChatGPT icons": pequeños, juntos, tipo chip */
      div.stButton > button {
        padding: 0.10rem 0.35rem !important;
        font-size: 0.95rem !important;
        border-radius: 999px !important;
        min-height: 28px !important;
        line-height: 1 !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        background: rgba(255,255,255,0.04) !important;
      }
      div.stButton { margin: 0 !important; }
      div[data-testid="column"] { padding-left: 0.06rem !important; padding-right: 0.06rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Draft")
st.caption("Agente para redactar tarjetas de funcionalidad y bugs.")

@st.cache_resource
def get_agent_app():
    return build_graph()

agent_app = get_agent_app()

# Estado conversación
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hola, soy **Draft**. Cuéntame qué necesitas (funcionalidad o bug) y te devuelvo la tarjeta lista.",
        }
    ]

# Estado de trabajo (tarjeta actual)
st.session_state.setdefault("last_card", None)
st.session_state.setdefault("last_fields", None)
st.session_state.setdefault("last_ticket_type", None)
st.session_state.setdefault("last_output_mode", None)

# Estado UX
st.session_state.setdefault("copied_flag", False)
st.session_state.setdefault("show_add_req", False)
st.session_state.setdefault("show_remove_req", False)

# Iconos
ICON_COPY = "⧉"
ICON_VALIDATION_REMOVE = "V ⌫"
ICON_VALIDATION_ADD = "V ✓"
ICON_ADD_REQ = "R ➕"
ICON_REMOVE_REQ = "R ➖"


def has_validation() -> bool:
    fields = st.session_state.get("last_fields") or {}
    return bool((fields.get("validation") or "").strip())


def is_small_talk(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return True

    small = [
        "gracias",
        "muchas gracias",
        "ok",
        "vale",
        "perfecto",
        "genial",
        "hola",
        "buenas",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "👍",
        "👌",
        "✅",
    ]
    if len(t) <= 20 and any(t == s or t.startswith(s) for s in small):
        return True
    return False


def run_agent(user_text: str):
    base_fields = st.session_state.get("last_fields") or {
        "title": "",
        "description": "",
        "requirements": "",
        "validation": "",
    }

    initial_state = {
        "raw_request": user_text,
        "fields": base_fields,
        "ticket_type": st.session_state.get("last_ticket_type") or "funcionalidad",
        "output_mode": st.session_state.get("last_output_mode") or "completa",
    }

    final_state = agent_app.invoke(initial_state)
    card = (final_state.get("card") or "").strip()
    return card, final_state.get("fields"), final_state.get("ticket_type"), final_state.get("output_mode")


def apply_instruction(instruction: str):
    card, fields, ticket_type, output_mode = run_agent(instruction)

    st.session_state.last_card = card
    if fields:
        st.session_state.last_fields = fields
    if ticket_type:
        st.session_state.last_ticket_type = ticket_type
    if output_mode:
        st.session_state.last_output_mode = output_mode

    # Log en chat (transparencia)
    st.session_state.messages.append({"role": "user", "content": instruction})
    st.session_state.messages.append({"role": "assistant", "content": "Aquí tienes la tarjeta:\n\n" + card})


# Render del chat
for msg in st.session_state.messages:
    avatar = "🧰" if msg["role"] == "assistant" else "🐵"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Input principal
user_input = st.chat_input("Escribe lo que necesitas…")

if user_input:
    # Mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🐵"):
        st.markdown(user_input)

    # Small talk detection (NO genera tarjeta)
    if is_small_talk(user_input):
        reply = (
            "Perfecto. Si quieres crear una tarjeta, dime la necesidad o el bug "
            "en una frase (módulo + qué pasa / qué se quiere)."
        )
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar="🧰"):
            st.markdown(reply)
        st.stop()

    # Ejecución normal del agente
    with st.chat_message("assistant", avatar="🧰"):
        with st.spinner("Draft está trabajando…"):
            try:
                card, fields, ticket_type, output_mode = run_agent(user_input)

                st.session_state.last_card = card
                if fields:
                    st.session_state.last_fields = fields
                if ticket_type:
                    st.session_state.last_ticket_type = ticket_type
                if output_mode:
                    st.session_state.last_output_mode = output_mode

                st.markdown("Aquí tienes la tarjeta:")
                st.markdown(card)

            except Exception as e:
                st.error(f"Error ejecutando Draft: {e}")

    st.session_state.messages.append(
        {"role": "assistant", "content": "Aquí tienes la tarjeta:\n\n" + (st.session_state.last_card or "")}
    )

# Toolbar compacta
if st.session_state.last_card:
    st.divider()

    c1, c2, c3, c4 = st.columns([0.55, 0.85, 0.75, 0.75])

    with c1:
        if st.button(ICON_COPY, help="Copiar tarjeta"):
            st.session_state.copied_flag = True

    with c2:
        if has_validation():
            if st.button(ICON_VALIDATION_REMOVE, help="Quitar validación"):
                apply_instruction("Quita la validación de esta tarjeta.")
                st.rerun()
        else:
            if st.button(ICON_VALIDATION_ADD, help="Añadir validación"):
                apply_instruction("Añade una validación adecuada a esta tarjeta (2-4 bullets verificables).")
                st.rerun()

    with c3:
        if st.button(ICON_ADD_REQ, help="Añadir requisito"):
            st.session_state.show_add_req = True
            st.session_state.show_remove_req = False

    with c4:
        if st.button(ICON_REMOVE_REQ, help="Quitar requisito"):
            st.session_state.show_remove_req = True
            st.session_state.show_add_req = False

    if st.session_state.copied_flag:
        st.success("Selecciona y copia la tarjeta (Ctrl+C).")
        st.text_area("Tarjeta", st.session_state.last_card, height=200)
        st.session_state.copied_flag = False

    # UI: añadir requisito
    if st.session_state.show_add_req:
        st.markdown("**Añadir requisito**")
        req = st.text_input(
            "Requisito",
            placeholder="Ej: Añadir paginación para evitar bloqueos…",
            key="add_req_input",
        )
        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("Aplicar"):
                if req and req.strip():
                    apply_instruction(f"Añade este requisito a la tarjeta: {req.strip()}")
                st.session_state.show_add_req = False
                st.rerun()
        with b2:
            if st.button("Cancelar"):
                st.session_state.show_add_req = False
                st.rerun()

    # UI: quitar requisito
    if st.session_state.show_remove_req:
        st.markdown("**Quitar requisito**")
        hint = st.text_input(
            "Texto a eliminar",
            placeholder="Ej: paginación / permisos / query…",
            key="remove_req_input",
        )
        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("Aplicar"):
                if hint and hint.strip():
                    apply_instruction(
                        f"Elimina de la tarjeta el requisito que contenga (o se refiera a): {hint.strip()}. "
                        f"Si hay varios parecidos, elimina el más relevante."
                    )
                st.session_state.show_remove_req = False
                st.rerun()
        with b2:
            if st.button("Cancelar"):
                st.session_state.show_remove_req = False
                st.rerun()

# Sidebar mínimo
with st.sidebar:
    st.markdown("### Controles")
    if st.button("Limpiar chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hola, soy **Draft**. Cuéntame qué necesitas (funcionalidad o bug) y te devuelvo la tarjeta lista.",
            }
        ]
        st.session_state.last_card = None
        st.session_state.last_fields = None
        st.session_state.last_ticket_type = None
        st.session_state.last_output_mode = None
        st.session_state.copied_flag = False
        st.session_state.show_add_req = False
        st.session_state.show_remove_req = False
        st.rerun()
