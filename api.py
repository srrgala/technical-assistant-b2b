# api.py — Servidor HTTP FastAPI para el asistente técnico Llana
#
# Expone procesar_consulta() como endpoint REST.
# El sistema es stateless por diseño: cada request es independiente.
# La concatenación de clarificación + respuesta del usuario es
# responsabilidad del cliente que integra este endpoint.
#
# Uso:
#   uvicorn api:app --host 0.0.0.0 --port 8000
#   uvicorn api:app --reload          # desarrollo local

from __future__ import annotations

import logging
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from main import procesar_consulta

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Asistente Técnico B2B — Llana",
    description=(
        "API para consultas técnicas sobre productos Llana. "
        "El sistema es stateless: cada request debe incluir la query completa. "
        "Si el asistente devuelve una pregunta de clarificación (empieza por '¿'), "
        "el cliente debe concatenar la pregunta original + la respuesta del usuario "
        "y reenviar como una sola query."
    ),
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_ALLOWED_ORIGINS = [
    "https://technical-assistant-b2b.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ConsultaRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Consulta técnica del usuario. Puede ser la query original o una concatenación.",
        examples=["¿Puedo usar Tixar Flex Duo S2 en exterior sobre hormigón?"],
    )


class ConsultaResponse(BaseModel):
    respuesta: str = Field(
        ...,
        description=(
            "Respuesta del asistente. Puede ser: "
            "(1) respuesta técnica, "
            "(2) pregunta de clarificación si faltan datos, "
            "(3) mensaje de fuera de alcance."
        ),
    )
    requiere_clarificacion: bool = Field(
        ...,
        description="True si la respuesta es una pregunta de clarificación y el cliente debe reenviar con contexto.",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse("index.html")


@app.get("/health", tags=["Sistema"])
@app.head("/health", include_in_schema=False)
def health() -> dict:
    """Comprueba que el servidor está operativo."""
    return {"status": "ok"}


@app.post(
    "/consulta",
    response_model=ConsultaResponse,
    tags=["Asistente"],
    summary="Procesar consulta técnica",
)
@limiter.limit("10/minute")
def consulta(request: Request, body: ConsultaRequest) -> ConsultaResponse:
    """
    Procesa una consulta técnica y devuelve la respuesta del asistente.

    **Flujo stateless:**
    1. Cliente envía query.
    2. Si `requiere_clarificacion` es `true`, concatenar la query original
       con la respuesta del usuario y reenviar: `"<query_original> <respuesta_usuario>"`.
    3. Repetir hasta que `requiere_clarificacion` sea `false`.
    """
    logger.info("Query recibida [len=%d]: %s", len(body.query), body.query[:120])

    try:
        resultado = procesar_consulta(body.query)
    except Exception as e:
        logger.exception("Error inesperado en procesar_consulta: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del asistente.")

    logger.info(
        "Respuesta generada [clarificacion=%s, len=%d]",
        resultado["requiere_clarificacion"],
        len(resultado["respuesta"]),
    )

    return ConsultaResponse(
        respuesta=resultado["respuesta"],
        requiere_clarificacion=resultado["requiere_clarificacion"],
    )
