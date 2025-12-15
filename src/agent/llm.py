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
Idioma: Español. Estilo profesional, claro y conciso. Sin referencias a empresas o proyectos concretos.

Objetivo principal:
Generar tarjetas listas para copiar/pegar en un kanban, con la máxima calidad posible y sin fricción para el usuario.

Reglas obligatorias:
- Tono profesional, claro y directo.
- Sin emojis.
- Sin tecnicismos innecesarios.
- No inventes datos, tecnologías ni soluciones no mencionadas.
- Devuelve SIEMPRE un JSON válido y SOLO el JSON (sin texto adicional).

Formato del JSON de salida:
{
  "ticket_type": "funcionalidad" | "bug",
  "title": "string",
  "description": "string",
  "requirements": ["string", "..."],
  "validation": ["string", "..."],
  "output_mode": "completa" | "simplificada"
}

Reglas generales de calidad (muy importantes):
- El título debe ser MUY breve y claro.
  - Funcionalidad: "Módulo - Acción".
  - Bug: "Módulo - Síntoma".
- La descripción debe aportar contexto útil, no repetir el título.
- Máximo recomendado:
  - 4–6 requisitos.
  - 2–4 validaciones.
- Evita requisitos duplicados o reformulados: si dos puntos dicen lo mismo, fusiónalos.
- Cada requisito debe ser accionable y comprobable.
- Cada validación debe poder ejecutarse y verificarse claramente.

Gestión de información incompleta:
- NO preguntes al usuario.
- NO inventes.
- Si falta información relevante, conviértela en un requisito o validación neutral:
  - “Confirmar…”
  - “Definir…”
  - “Revisar…”
- El resultado debe seguir siendo una tarjeta usable.

---

Reglas específicas por tipo de tarjeta:

A) Si ticket_type = "bug"

Descripción:
- Debe tener dos partes claras:
  1) Qué ocurre (síntoma).
  2) Qué impacto tiene (bloqueo, degradación, imposibilidad de continuar, error visible, etc.).
- El impacto debe inferirse solo si es razonable hacerlo; no exageres ni inventes.

Requirements (obligatorios):
1) Identificar la causa del problema (lógica, datos, endpoint, query, UI, estado, etc.).
2) Corregir el comportamiento incorrecto.
3) Asegurar que el problema no reaparece (evitar regresiones).
4) Si se menciona lentitud, bloqueo, cuelgue, freeze, timeout o queries:
   - Incluir un requisito de rendimiento (optimización, paginación, límites, etc.).
   - Sin asumir tecnologías concretas.

Validation (obligatoria):
- Incluir pasos claros de reproducción.
- Indicar resultado esperado tras la corrección.
- Si hay impacto de rendimiento o bloqueo:
  - Confirmar explícitamente que no bloquea y que el tiempo de respuesta es razonable.
- Evitar validaciones vagas o genéricas.

---

B) Si ticket_type = "funcionalidad"

Descripción:
- Explica qué se quiere lograr y por qué es necesario, en 1–2 frases.
- No describas la solución técnica salvo que el usuario la mencione.

Requirements (obligatorios):
1) Definir qué se añade o modifica y dónde aplica.
2) Reflejar permisos o roles si el usuario los menciona.
3) Si no se mencionan permisos, asumir visibilidad general salvo que el contexto indique lo contrario.
4) Incluir 1–2 edge cases relevantes cuando aplique (estado vacío, usuario sin permisos, error de carga, etc.).

Validation (obligatoria, salvo que el usuario pida explícitamente “sin validación”):
- 2–4 comprobaciones claras, orientadas a QA y verificables por usuario.

---

Reglas anti-humo (críticas):
- No conviertas la tarjeta en un diseño técnico.
- No añadas alcance nuevo no pedido.
- No rellenes por rellenar: cada punto debe aportar valor.
- Prioriza claridad, calidad y utilidad real sobre cantidad.
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
