# identity.py — Gestiona saludos y preguntas sobre la identidad del asistente

KEYWORDS_SALUDO = [
    "hola", "buenos días", "buenas tardes", "buenas noches", "buenas",
    "hey", "hi", "hello", "qué tal", "que tal", "cómo estás", "como estas",
    "cómo va", "como va", "qué hay", "que hay",
]

KEYWORDS_IDENTIDAD = [
    "quién eres", "quien eres", "qué eres", "que eres",
    "cómo te llamas", "como te llamas", "cuál es tu nombre", "cual es tu nombre",
    "qué puedes hacer", "que puedes hacer", "para qué sirves", "para que sirves",
    "cómo funcionas", "como funcionas", "qué sabes", "que sabes",
    "eres una ia", "eres un bot", "eres humano", "eres una inteligencia",
]

RESPUESTA_SALUDO = (
    "¡Hola! Soy el asistente técnico de Llana. "
    "Estoy aquí para resolver tus dudas sobre aplicación y uso de nuestros productos. "
    "¿En qué puedo ayudarte?"
)

RESPUESTA_IDENTIDAD = (
    "Soy un asistente técnico especializado en productos Llana. "
    "Puedo ayudarte con dudas sobre aplicación, compatibilidad de soportes, "
    "entornos de uso y recomendaciones técnicas de los siguientes productos: "
    "Juncta Epox RG-2, Juncta Mineral CG2-WA, Tixar Flex Duo S2, "
    "Tixar Gel Mono S1, Cobertec Vial Ligero y Cobertec Pool. "
    "¿Tienes alguna consulta técnica?"
)


def _normalizar(texto: str) -> str:
    return texto.lower().strip()


def detectar_tipo(query: str) -> str | None:
    """
    Devuelve 'saludo', 'identidad' o None si no aplica.
    """
    query_norm = _normalizar(query)

    if any(kw in query_norm for kw in KEYWORDS_SALUDO):
        return "saludo"

    if any(kw in query_norm for kw in KEYWORDS_IDENTIDAD):
        return "identidad"

    return None


def responder(tipo: str) -> str:
    if tipo == "saludo":
        return RESPUESTA_SALUDO
    if tipo == "identidad":
        return RESPUESTA_IDENTIDAD
    return RESPUESTA_SALUDO
