# responder.py — Construye respuestas siguiendo la estructura obligatoria del spec
# Estructura: 1. Respuesta directa  2. Explicación breve  3. Recomendación  4. Referencia

from __future__ import annotations

import logging
from pathlib import Path

import anthropic

from config import PRODUCTOS_VALIDOS
from core import fallback

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
MIN_FRAGMENTOS = 1
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

# ---------------------------------------------------------------------------
# Cliente Anthropic (instanciado una vez, reutilizado en cada llamada)
# ---------------------------------------------------------------------------
_client = anthropic.Anthropic()

# ---------------------------------------------------------------------------
# System prompt — cargado una vez al arranque del módulo
# Path absoluto desde la ubicación del archivo para evitar dependencia
# del directorio de trabajo del proceso.
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT: str = (
    Path(__file__).parent.parent / "prompts" / "system_prompt.txt"
).read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Tool de respuesta estructurada
# Elimina la heurística startswith("¿") — el LLM declara explícitamente
# si la respuesta es una clarificación o una respuesta técnica definitiva.
# ---------------------------------------------------------------------------
_RESPONSE_TOOL = {
    "name": "provide_response",
    "description": "Proporciona la respuesta técnica estructurada al usuario.",
    "input_schema": {
        "type": "object",
        "properties": {
            "respuesta": {
                "type": "string",
                "description": (
                    "Respuesta técnica completa siguiendo la estructura obligatoria: "
                    "1. Respuesta directa. 2. Explicación breve. "
                    "3. Recomendación. 4. Referencia."
                ),
            },
            "requiere_clarificacion": {
                "type": "boolean",
                "description": (
                    "True si la documentación disponible no es suficiente para responder "
                    "con seguridad y se necesita más contexto del usuario. "
                    "False en cualquier otro caso."
                ),
            },
        },
        "required": ["respuesta", "requiere_clarificacion"],
    },
}


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def construir_respuesta(query: str, producto_id: str, contexto: str | None) -> dict:
    """
    Construye la respuesta final siguiendo la estructura del spec.
    Devuelve siempre un dict con claves 'respuesta' y 'requiere_clarificacion'.

    Si el contexto es None o vacío → fallback sin_informacion, clarificacion=False.
    Si hay contexto → llama al LLM con el prompt estructurado.
    Si la llamada a la API falla → fallback baja_confianza, clarificacion=False.
    """
    if not contexto:
        return {
            "respuesta": f"{fallback.sin_informacion()}\n\n{fallback.derivacion()}",
            "requiere_clarificacion": False,
        }

    nombre_producto = PRODUCTOS_VALIDOS[producto_id]["nombre_completo"]
    return _llamar_llm(query, nombre_producto, contexto)


# ---------------------------------------------------------------------------
# Lógica interna
# ---------------------------------------------------------------------------

def _llamar_llm(query: str, nombre_producto: str, contexto: str) -> dict:
    """
    Llama al LLM con tool_choice forzado.
    Devuelve dict con 'respuesta' y 'requiere_clarificacion'.
    En caso de error de API devuelve fallback con clarificacion=False.
    """
    user_message = (
        f"PRODUCTO: {nombre_producto}\n\n"
        f"DOCUMENTACIÓN TÉCNICA RELEVANTE:\n{contexto}\n\n"
        f"CONSULTA DEL USUARIO: {query}"
    )

    try:
        response = _client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[{"type": "text", "text": _SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            tools=[_RESPONSE_TOOL],
            tool_choice={"type": "tool", "name": "provide_response"},
            messages=[{"role": "user", "content": user_message}],
        )
        tool_block = next(b for b in response.content if b.type == "tool_use")
        return {
            "respuesta": tool_block.input["respuesta"],
            "requiere_clarificacion": bool(tool_block.input["requiere_clarificacion"]),
        }

    except anthropic.AuthenticationError:
        logger.error("ANTHROPIC_API_KEY inválida o no configurada.")
        return {"respuesta": fallback.baja_confianza(), "requiere_clarificacion": False}

    except anthropic.RateLimitError:
        logger.warning("Rate limit alcanzado en la API de Anthropic.")
        return {"respuesta": fallback.baja_confianza(), "requiere_clarificacion": False}

    except anthropic.APIStatusError as e:
        logger.error("Error de API de Anthropic [status=%s]: %s", e.status_code, e.message)
        return {"respuesta": fallback.baja_confianza(), "requiere_clarificacion": False}

    except Exception as e:
        logger.exception("Error inesperado al llamar al LLM: %s", e)
        return {"respuesta": fallback.baja_confianza(), "requiere_clarificacion": False}
