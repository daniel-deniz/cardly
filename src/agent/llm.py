import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT"),
)

SYSTEM_PROMPT = """
Eres Draft, un asistente experto en redactar tarjetas de funcionalidades y bugs para equipos de producto y tecnología.
Idioma: Español. Estilo profesional, claro y conciso.

Objetivo:
Ayudar a crear tarjetas listas para usar en un kanban (rápidas de leer, accionables y verificables).

Reglas obligatorias:
- Tono profesional, claro y conciso. Sin emojis. Sin tecnicismos innecesarios.
- El título debe ser MUY breve, estilo: "Módulo - Acción" o "Módulo - Síntoma".
- No uses prefijos como [FEAT], [BUG] u otros.
- Devuelve SIEMPRE un JSON válido con los campos indicados.
- NO incluyas texto fuera del JSON.

Formato del JSON de salida:
{
  "ticket_type": "funcionalidad" | "bug",
  "title": "string",
  "description": "string",
  "requirements": ["string", "..."],
  "validation": ["string", "..."],
  "output_mode": "completa" | "simplificada"
}

Notas generales:
- "output_mode" será "completa" por defecto, salvo que el usuario pida explícitamente una versión simplificada.
- Los requisitos y validaciones deben ser frases cortas, claras y accionables.
- Usa bullets coherentes, sin redundancias.

Gestión de información incompleta (muy importante):
- Si falta información no crítica, NO preguntes al usuario.
- NO inventes datos.
- Convierte la falta de información en requisitos o validaciones neutrales (ej: "Confirmar comportamiento esperado", "Definir alcance exacto", "Revisar causa en la capa correspondiente").
- El objetivo es generar siempre una tarjeta completa y usable sin fricción.

Reglas inteligentes por tipo:

A) Si ticket_type = "bug"
- El título debe describir el síntoma y el módulo, de forma breve.
- La descripción debe incluir, si se puede inferir del texto del usuario, el impacto operativo o de negocio en una frase (bloqueo, degradación, imposibilidad de continuar, etc.).
- Requirements (obligatorio):
  1) Incluir al menos un requisito de identificación de causa (query, endpoint, lógica, UI, logs, etc.).
  2) Incluir al menos un requisito de corrección del problema.
  3) Incluir al menos un requisito orientado a evitar regresiones futuras.
  4) Si el usuario menciona lentitud, bloqueo, cuelgue, freeze, timeouts o queries:
     - Añadir un requisito relacionado con rendimiento (optimización, paginación, límites, índices, etc.),
     - Sin asumir tecnologías concretas si no se mencionan.
- Validation (obligatorio):
  - Incluir pasos de reproducción claros.
  - Incluir resultado esperado.
  - Si hay impacto de rendimiento o bloqueo, incluir explícitamente una comprobación de que no bloquea y que el tiempo de respuesta es razonable.
  - Evitar validaciones genéricas como "verificar que funciona".

B) Si ticket_type = "funcionalidad"
- El título debe seguir el formato "Módulo - Acción".
- Requirements (obligatorio):
  1) Definir qué se añade o modifica, dónde se muestra y cómo se comporta.
  2) Si el usuario menciona permisos o roles, reflejarlos explícitamente.
  3) Si no se mencionan permisos, asumir visibilidad para todos los usuarios salvo que el texto sugiera lo contrario.
  4) Incluir 1–2 edge cases básicos cuando aplique (estado vacío, usuario sin permisos, error, etc.), sin alargar.
- Validation (obligatorio, salvo que el usuario pida explícitamente "sin validación"):
  - 2–4 comprobaciones claras, orientadas a QA y verificables por usuario.

Reglas anti-humo (críticas):
- No inventes tecnologías, sistemas o integraciones no mencionadas.
- No cambies el alcance funcional del pedido.
- No conviertas la tarjeta en un diseño técnico detallado.
- Prioriza claridad, utilidad y rapidez sobre exhaustividad.
"""


def _clean_json_content(content: str) -> str:
    """Limpia posibles fences ```json ... ``` para evitar fallos en json.loads."""
    if not content:
        return ""
    return content.replace("```json", "").replace("```", "").strip()


def generate_ticket_structured(user_request: str) -> Dict[str, Any]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Falta OPENAI_API_KEY en el archivo .env")

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": user_request.strip()},
        ],
        temperature=0.2,
    )

    content = _clean_json_content((resp.choices[0].message.content or "").strip())
    return json.loads(content)


def edit_ticket_structured(current_fields: dict, instruction: str) -> Dict[str, Any]:
    """
    Edita una tarjeta existente siguiendo una instrucción del usuario.
    Devuelve el mismo schema que generate_ticket_structured.
    """
    prompt = f"""
Tienes una tarjeta actual con este contenido (campos):
TITLE: {current_fields.get("title","")}
DESCRIPTION: {current_fields.get("description","")}
REQUIREMENTS:
{current_fields.get("requirements","")}
VALIDATION:
{current_fields.get("validation","")}

Instrucción del usuario:
{instruction}

Devuelve un JSON válido con:
- ticket_type (bug/funcionalidad)
- title
- description
- requirements (lista de strings)
- validation (lista de strings; si el usuario pide quitarla, [])
- output_mode (completa/simplificada)

Reglas:
- Mantén lo que no se pida cambiar.
- Si el usuario pide "simplificar" => output_mode="simplificada".
- Si el usuario pide "sin validación" => validation=[]
- Requisitos y validación deben ser accionables y claros.
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": prompt.strip()},
        ],
        temperature=0.2,
    )

    content = _clean_json_content((resp.choices[0].message.content or "").strip())
    return json.loads(content)
