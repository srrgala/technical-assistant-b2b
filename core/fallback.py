# fallback.py — Textos de fallback exactos según el spec. No modificar por consulta.

FALLBACK_SIN_INFORMACION = (
    "No dispongo de información suficiente para responder con precisión."
)

FALLBACK_FUERA_DE_ALCANCE = (
    "Esta consulta está fuera del alcance del asistente técnico. "
    "Solo puedo asesorarte sobre adhesivos cerámicos, morteros de junta "
    "e impermeabilización de la gama Llana."
)

FALLBACK_FUERA_DE_ALCANCE_RECOMENDACION = (
    "No hago recomendaciones de qué producto elegir dentro del catálogo "
    "— resuelvo consultas técnicas sobre un producto concreto. "
    "Indícame con qué producto estás trabajando y te ayudo con el detalle técnico."
)

FALLBACK_BAJA_CONFIANZA = (
    "Prefiero no darte una respuesta incorrecta."
)

FALLBACK_DERIVACION = (
    "Te recomiendo contactar con el equipo técnico de Llana."
)


def sin_informacion() -> str:
    return FALLBACK_SIN_INFORMACION


def fuera_de_alcance() -> str:
    return FALLBACK_FUERA_DE_ALCANCE


def fuera_de_alcance_recomendacion() -> str:
    return FALLBACK_FUERA_DE_ALCANCE_RECOMENDACION


def baja_confianza() -> str:
    return FALLBACK_BAJA_CONFIANZA


def derivacion() -> str:
    return FALLBACK_DERIVACION
