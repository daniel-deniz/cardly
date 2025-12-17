# src/release_email.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class ReleaseEmailResult:
    subject: str
    body: str
    warnings: list[str]


FIX_KEYWORDS = [
    "error",
    "fallo",
    "bug",
    "fix",
    "corrige",
    "corregir",
    "corrección",
    "no funciona",
    "problema",
]

EMAIL_SUBJECT = "📢 ¡Nueva versión disponible del Portal!"


def _looks_like_fix(text: str) -> bool:
    """Heurística simple y conservadora para detectar si una tarjeta parece corrección."""
    t = (text or "").lower().strip()
    if not t:
        return False
    return any(k in t for k in FIX_KEYWORDS)


def _html_to_text_keep_lines(text: str) -> str:
    """Convierte HTML 'simple' a texto conservando saltos típicos."""
    if not text:
        return ""
    t = text

    # Saltos HTML a \n
    t = t.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    t = t.replace("</br>", "\n")

    # Quitar tags (a, strong, i, etc.)
    t = re.sub(r"<[^>]+>", " ", t)

    # Unescape mínimo
    t = t.replace("&nbsp;", " ").replace("&amp;", "&")

    # Normalizar saltos
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    return t


def _clean_description(text: str) -> str:
    """Limpieza agresiva de descripciones que vienen de portales (HTML, links, ramas, etc.)."""
    if not text:
        return ""

    t = _html_to_text_keep_lines(text)

    # Cortar bloques técnicos largos (para email cliente)
    for marker in [
        "Causa raíz:",
        "Problema actual:",
        "Ejemplo de logs",
        "Logs:",
        "Solución requerida:",
        "Tareas:",
        "Impacto:",
        "Query actual:",
    ]:
        idx = t.lower().find(marker.lower())
        if idx != -1:
            t = t[:idx]
            break

    # Si hay bloques de código, cortar antes
    if "```" in t:
        t = t.split("```", 1)[0]

    # Cortar secciones internas típicas (para cliente no aportan)
    for marker in ["Requisitos:", "Validación:", "Validation:", "Requirements:"]:
        if marker in t:
            t = t.split(marker, 1)[0]

    lines = [l.strip() for l in t.split("\n")]
    kept: list[str] = []

    for l in lines:
        if not l:
            continue

        low = l.lower()

        # Filtra URLs y ruido típico
        if "http://" in low or "https://" in low or "github.com" in low:
            continue
        if "pull request" in low:
            continue

        # Filtra ramas y prefijos de dev (líneas completas)
        if low.startswith(("feature/", "fix/", "hotfix/", "release/")):
            continue
        if low.startswith(("portal:", "ninja:", "github:", "branch:", "pr:")):
            continue

        # Filtra líneas que son solo "Ticket #..."
        if low.startswith("ticket #") or low.startswith("ticket#"):
            continue

        kept.append(l)

    cleaned = " ".join(kept)

    # Quitar referencias técnicas embebidas (ramas/tags)
    cleaned = re.sub(r"\bclaude/[^\s]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(rama\s*->\s*)?feature/[^\s]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bfix/[^\s]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bhotfix/[^\s]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\brelease/[^\s]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bFF:\s*[^\s]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\breplace-[a-z0-9-]+\b", "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.replace("**", "")
    return cleaned


def _clean_title(title: str) -> str:
    """Limpieza leve de título. No inventa, solo quita ruido."""
    t = (title or "").strip()
    t = re.sub(r"^ticket\s*#\d+\s*-\s*", "", t, flags=re.IGNORECASE).strip()
    return t


def _normalize_cards(cards_or_payload: Any) -> list[dict[str, Any]]:
    """
    Soporta:
      - lista de dicts (cards)
      - dict con clave 'tasks' (payload del portal)
    """
    if isinstance(cards_or_payload, dict) and "tasks" in cards_or_payload:
        tasks = cards_or_payload.get("tasks")
        return list(tasks or [])
    if isinstance(cards_or_payload, list):
        return cards_or_payload
    return []


def _llm_client_friendly(text: str, llm_rewriter: Optional[Callable[[str], str]] = None) -> str:
    """
    Reescribe una descripción en lenguaje cliente (1–2 frases), SIN inventar.
    Si no hay llm_rewriter, devuelve el texto original.
    """
    t = (text or "").strip()
    if not t or llm_rewriter is None:
        return t

    prompt = f"""
Eres un asistente que limpia texto técnico para un email de release a cliente.

INSTRUCCIONES (OBLIGATORIAS):
- Reescribe en español para cliente.
- Máximo 2 frases.
- Usa SIEMPRE pasado o presente.
- Usa voz activa y directa: "Se ha añadido", "Se han añadido", "Se ha corregido", "Se ha optimizado".
- NO incluyas frases de diagnóstico o detección ("se ha detectado", "se identificó", "se observó").
- NO uses futuro.
- NO inventes información.
- NO añadas beneficios genéricos ("mejor experiencia", "mayor estabilidad") si no están explícitos.
- Mantén concordancia gramatical correcta (singular/plural).
- Elimina referencias técnicas: ramas, PR, IDs, logs, SQL, endpoints, nombres de clases.
- Si el texto no tiene contenido funcional claro, devuelve exactamente: "Mejora interna."

TEXTO:
{t}
""".strip()

    out = (llm_rewriter(prompt) or "").strip()
    return out or t


def generate_release_email(
    version_name: str,
    cards: Any,
    product_name: str = "Portal",
    max_news: int = 50,
    max_fixes: int = 50,
    llm_rewriter: Optional[Callable[[str], str]] = None,
) -> ReleaseEmailResult:
    warnings: list[str] = []

    if not version_name:
        warnings.append("Falta version_name. Se ha generado un asunto genérico.")
        version_name = "sin versión"

    cards_list = _normalize_cards(cards)
    if not cards_list:
        raise ValueError("No hay tarjetas en la versión. No se puede generar email.")

    # Filtrado mínimo: solo incompletas (sin título)
    visible_cards: list[dict[str, Any]] = []
    excluded: list[str] = []
    missing_desc = 0

    for c in cards_list:
        title = (c.get("title") or "").strip()
        desc = (c.get("description") or "").strip()

        if not title:
            excluded.append("Sin título (incompleta)")
            continue

        if not desc:
            missing_desc += 1

        visible_cards.append(c)

    if excluded:
        warnings.append(f"Se han excluido {len(excluded)} tarjetas (incompletas).")
        warnings.append("Excluidas: " + " | ".join(excluded))

    if missing_desc > 0:
        warnings.append(f"Revisar: faltan descripciones en {missing_desc} tarjeta(s).")

    # Clasificación Novedades vs Correcciones
    news: list[dict[str, Any]] = []
    fixes: list[dict[str, Any]] = []

    for c in visible_cards:
        type_raw = (c.get("type") or "").strip().lower()

        if type_raw:
            if "bug" in type_raw or "corre" in type_raw:
                fixes.append(c)
            else:
                news.append(c)
        else:
            combined = f"{c.get('title') or ''} {c.get('description') or ''}"
            if _looks_like_fix(combined):
                fixes.append(c)
            else:
                news.append(c)

    # Limitar volumen (por si un release viene gigante)
    more_news = max(0, len(news) - max_news)
    more_fixes = max(0, len(fixes) - max_fixes)
    news = news[:max_news]
    fixes = fixes[:max_fixes]
    if more_news + more_fixes > 0:
        warnings.append("Se ha resumido el release por volumen. Revisa si deseas más detalle.")

    def bullet(c: dict[str, Any]) -> str:
        title = _clean_title(c.get("title") or "")
        desc = _clean_description(c.get("description") or "")
        desc = _llm_client_friendly(desc, llm_rewriter)
        return f"- **{title}**: {desc}" if desc else f"- **{title}**"

    subject = EMAIL_SUBJECT

    lines: list[str] = []
    lines.append("Buenas tardes,")
    lines.append("")
    lines.append(
        "Les informamos que ya se encuentra disponible una nueva versión del Portal, "
        "desarrollada teniendo en cuenta distintas solicitudes de mejora. "
        "Esta actualización incorpora funcionalidades clave y correcciones orientadas a mejorar la operativa diaria."
    )
    lines.append("")

    if news:
        lines.append("**Novedades**")
        for c in news:
            lines.append(bullet(c))
        if more_news > 0:
            lines.append(f"- Y otras {more_news} mejoras menores.")
        lines.append("")

    if fixes:
        lines.append("**Correcciones**")
        for c in fixes:
            lines.append(bullet(c))
        if more_fixes > 0:
            lines.append(f"- Y otras {more_fixes} correcciones menores.")
        lines.append("")

    lines.append(
        "Estas mejoras están diseñadas para optimizar el uso del Portal y ofrecer una experiencia más precisa, segura y eficiente."
    )
    lines.append("")
    lines.append("Un saludo,")

    body = "\n".join(lines) + "\n"
    return ReleaseEmailResult(subject=subject, body=body, warnings=warnings)
