from agent.graph import build_graph


def main():
    app = build_graph()

    print("Agente de Tarjetas (MVP) — escribe una petición breve.\n")
    raw = input("Petición: ").strip()

    # De momento no extraemos campos del texto; el agente preguntará lo que falte.
    initial_state = {
        "raw_request": raw,
        "fields": {
            "title": "",
            "description": raw,   # usamos tu petición como descripción inicial
            "requirements": "",
            "validation": "",
        },
    }

    final_state = app.invoke(initial_state)

    print("\n--- TARJETA GENERADA ---\n")
    print(final_state["card"])


if __name__ == "__main__":
    main()
