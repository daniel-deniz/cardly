# Release 2.3 — Email de release a cliente

## Qué incluye
- Generación de emails de release a partir de JSON reales del portal
- Limpieza agresiva de HTML y ruido técnico
- Clasificación automática:
  - Novedades
  - Correcciones
- Reescritura de descripciones en lenguaje cliente:
  - Máximo 2 frases
  - Sin inventar información
- Asunto fijo y cuerpo listo para copiar/pegar
- Visualización directa del email dentro del chat (Streamlit)

## Decisiones de producto
- Draft actúa como **asistente**, no como agente autónomo
- No se integran APIs externas (input por copy/paste)
- No se ocultan tarjetas “internas” por heurística
- El LLM solo se usa para reescritura, no para clasificación ni filtrado
- UX simple, orientada a uso real

## Qué se considera fuera de alcance
- Envío automático de emails
- Gestión de versiones o histórico
- Agrupaciones complejas o inteligencia contextual
- Personalización del contenido por cliente

## Estado
✅ DONE  
La versión cumple su objetivo y no se ampliará salvo correcciones reales.