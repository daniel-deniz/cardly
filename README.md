# Draft – av-cards

Draft es un asistente de IA orientado a equipos de producto y tecnología.
Su objetivo es transformar información poco estructurada en contenido claro,
accionable y listo para usar en contextos reales (backlog, QA, comunicación interna).

Este repositorio contiene el núcleo lógico del asistente Draft.

---

## Qué es Draft

Draft no es un chatbot genérico.
Es un asistente con reglas de producto claras, diseñado para:

- reducir ambigüedad en requisitos
- mejorar la calidad de las tarjetas de trabajo
- ahorrar tiempo en la redacción y revisión de tickets

Draft prioriza claridad, consistencia y utilidad real.
No inventa información ni rellena contenido sin valor.

---

## Estado actual

Draft funciona actualmente como un **asistente de IA especializado en producto**.

Incluye:
- Generación de tarjetas de **Funcionalidad**
- Generación de tarjetas de **Bug / Corrección**
- Generación de **emails de release a cliente** a partir de JSON reales del portal (versión 2.3)

La herramienta se ejecuta en local mediante una interfaz en **Streamlit** y responde siempre a inputs explícitos del usuario (sin autonomía).

---

## Qué hace actualmente

Draft funciona como un asistente conversacional por estados que:

- Detecta la intención del usuario:
  - solicitud de tarjeta (Funcionalidad o Bug)
  - small talk u otros mensajes no relevantes
- Genera tarjetas estructuradas con formato estándar:
  - Título
  - Descripción
  - Requisitos
  - Validación
- Aplica reglas de producto, entre ellas:
  - evitar invención de datos
  - limitar contenido innecesario
  - convertir información incompleta en requisitos neutrales
  - mantener consistencia entre tarjetas

El resultado es contenido listo para copiar y pegar en herramientas de trabajo.

---

## Release Email (v2.3)

Draft incluye un motor de generación de emails de release orientados a cliente:

- Acepta JSON reales exportados del portal
- Limpia HTML y ruido técnico
- Clasifica tarjetas en **Novedades** y **Correcciones**
- Reescribe descripciones en lenguaje cliente (máx. 2 frases, sin inventar)
- Muestra el resultado directamente en la interfaz para copiar y enviar

El asunto del email es fijo y el contenido está pensado para ser **usable sin edición adicional**.

---

## Qué no hace todavía

- No envía emails de forma automática (el resultado es copy/paste)
- No gestiona versiones ni releases de manera autónoma
- No persiste histórico de tarjetas o releases
- No se integra directamente con APIs externas del portal
- No ejecuta acciones sin intervención humana

---

## Estructura del proyecto

```text
src/
├── llm.py      # Conexión y configuración del modelo de IA
├── state.py    # Estado de la conversación
├── nodes.py    # Lógica de negocio de Draft
├── graph.py    # Flujo del asistente
├── app.py      # Interfaz Streamlit
├── release_email.py  # Motor de generación de emails de release
