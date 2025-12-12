from agent.graph import build_graph


def main():
    app = build_graph()

    print("Agente de Tarjetas (MVP) — describe la necesidad o el bug.\n")
    raw = input("Petición: ").strip()

    initial_state = {
        "raw_request": raw,
        "fields": {
            "title": "",
            "description": raw,   # base
            "requirements": "",
            "validation": "",
        },
    }

    final_state = app.invoke(initial_state)

    print("\n--- TARJETA GENERADA ---\n")
    print(final_state["card"])


if __name__ == "__main__":
    main()
    