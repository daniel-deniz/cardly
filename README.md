# Draft – av-cards

Draft es un agente de IA orientado a equipos de producto y tecnología.
Su objetivo es transformar información poco estructurada en tarjetas claras,
accionables y listas para usar en contextos reales (backlog, QA, comunicación interna).

Este repositorio contiene el núcleo lógico del agente Draft.

---

## Qué es Draft

Draft no es un chatbot genérico.
Es un agente con reglas de producto claras, diseñado para:

- reducir ambigüedad en requisitos
- mejorar la calidad de las tarjetas de trabajo
- ahorrar tiempo en la redacción y revisión de tickets

Draft prioriza claridad, consistencia y utilidad real.
No inventa información ni rellena contenido sin valor.

---

## Qué hace actualmente

Draft funciona como un agente conversacional por estados que:

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

## Qué no hace todavía

- No envía emails ni comunicaciones automáticas
- No gestiona versiones ni releases
- No tiene interfaz gráfica
- No persiste información
- No se integra con herramientas externas

---

## Estructura del proyecto

```text
src/
├── llm.py      # Conexión y configuración del modelo de IA
├── state.py    # Estado de la conversación
├── nodes.py    # Lógica de negocio de Draft
└── graph.py    # Flujo del agente
