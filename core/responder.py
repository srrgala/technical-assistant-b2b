# responder.py — Construye respuestas siguiendo la estructura obligatoria del spec
# Estructura: 1. Respuesta directa  2. Explicación breve  3. Recomendación  4. Referencia

from __future__ import annotations

import logging
import os

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
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 1024

# ---------------------------------------------------------------------------
# Cliente Anthropic (instanciado una vez, reutilizado en cada llamada)
# ---------------------------------------------------------------------------
# El SDK lee ANTHROPIC_API_KEY del entorno automáticamente.
# Si la variable no existe, lanza anthropic.AuthenticationError en la primera llamada.
_client = anthropic.Anthropic()


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def construir_respuesta(query: str, producto_id: str, contexto: str | None) -> str:
    """
    Construye la respuesta final siguiendo la estructura del spec.

    Si el contexto es None o vacío → activa fallback sin_informacion + derivacion.
    Si hay contexto → llama al LLM con el prompt estructurado.
    Si la llamada a la API falla → loggea el error y devuelve fallback baja_confianza.
    """
    if not contexto:
        return _respuesta_sin_contexto()

    nombre_producto = PRODUCTOS_VALIDOS[producto_id]["nombre_completo"]
    return _llamar_llm(query, nombre_producto, contexto)


# ---------------------------------------------------------------------------
# Lógica interna
# ---------------------------------------------------------------------------

def _respuesta_sin_contexto() -> str:
    return f"{fallback.sin_informacion()}\n\n{fallback.derivacion()}"


def _llamar_llm(query: str, nombre_producto: str, contexto: str) -> str:
    """
    Llama al LLM con el system prompt del spec y el contexto recuperado.
    En caso de error de API devuelve fallback silencioso (el usuario no ve el error).
    """
    system_prompt, user_message = construir_prompt_llm(query, nombre_producto, contexto)

    try:
        message = _client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ],
        )
        return message.content[0].text

    except anthropic.AuthenticationError:
        logger.error("ANTHROPIC_API_KEY inválida o no configurada.")
        return fallback.baja_confianza()

    except anthropic.RateLimitError:
        logger.warning("Rate limit alcanzado en la API de Anthropic.")
        return fallback.baja_confianza()

    except anthropic.APIStatusError as e:
        logger.error("Error de API de Anthropic [status=%s]: %s", e.status_code, e.message)
        return fallback.baja_confianza()

    except Exception as e:
        logger.exception("Error inesperado al llamar al LLM: %s", e)
        return fallback.baja_confianza()


def construir_prompt_llm(query: str, nombre_producto: str, contexto: str) -> tuple[str, str]:
    """
    Genera el system prompt y el user message para enviar al LLM.

    Devuelve una tupla (system_prompt, user_message) para respetar
    la separación de roles que exige la API de Anthropic.
    """
    with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    user_message = (
        f"PRODUCTO: {nombre_producto}\n\n"
        f"DOCUMENTACIÓN TÉCNICA RELEVANTE:\n{contexto}\n\n"
        f"CONSULTA DEL USUARIO: {query}"
    )

    return system_prompt, user_message
