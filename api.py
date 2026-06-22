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
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from main import procesar_consulta

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
def consulta(body: ConsultaRequest) -> ConsultaResponse:
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
