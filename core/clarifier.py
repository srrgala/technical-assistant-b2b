# clarifier.py — Genera una sola pregunta por la primera variable crítica faltante.
# Regla estricta: una variable por turno, nunca lista de productos, nunca pregunta compuesta.

PREGUNTAS = {
    "producto":        "¿Con qué producto estás trabajando?",
    "soporte":         "¿Sobre qué tipo de superficie o soporte vas a aplicarlo?",
    "entorno":         "¿El uso es en interior, exterior, o en un entorno especial como piscina o zona de tráfico?",
    "superficie":      "¿Sobre qué tipo de superficie vas a intervenir?",
    "uso":             "¿Cuál es el uso previsto de la zona? Por ejemplo: parking, garaje, pasillo, rampa.",
    "nivel_exigencia": "¿Cuál es el nivel de exigencia o tráfico previsto? Por ejemplo: ligero, medio, intenso.",
    "objetivo":        "¿Cuál es el objetivo de la intervención: impermeabilizar, rehabilitar, aislar u otro?",
}

# Versiones más explícitas con opciones concretas para cuando el usuario
# ha respondido algo ambiguo y el sistema no pudo interpretar su respuesta
PREGUNTAS_DETALLADAS = {
    "producto": (
        "No he podido identificar el producto. "
        "¿Estás trabajando con Juncta Epox RG-2, Juncta Mineral CG2-WA, "
        "Tixar Flex Duo S2, Tixar Gel Mono S1, Cobertec Vial Ligero "
        "o Cobertec Pool?"
    ),
    "soporte": (
        "Necesito saber el soporte exacto. "
        "¿Es hormigón, cerámica, gres porcelánico, madera, yeso, mármol u otro material?"
    ),
    "entorno": (
        "Necesito que especifiques el entorno de uso. "
        "¿Es interior, exterior, piscina, fachada, terraza o zona con agua?"
    ),
    "superficie": (
        "¿Sobre qué superficie exacta vas a aplicarlo? "
        "Por ejemplo: hormigón, cerámica existente, madera, yeso."
    ),
    "uso": (
        "¿Para qué se usará la zona? "
        "Por ejemplo: garaje privado, parking comunitario, pasillo, rampa de acceso."
    ),
    "nivel_exigencia": (
        "¿Cuál es el nivel de tráfico previsto? "
        "Tráfico ligero (coches particulares ocasionales), medio o intenso."
    ),
}


def generar_pregunta(clasificacion: dict) -> str:
    """
    Genera la pregunta de clarificación adecuada.
    Si la query ya contiene una pregunta anterior (es una concatenación),
    usa la versión detallada para guiar mejor al usuario.
    """
    producto_id = clasificacion.get("producto_id")
    query = clasificacion.get("query_original", "")

    if producto_id is None:
        # Si la query es larga, es probable que sea una concatenación fallida
        if len(query) > 30:
            return PREGUNTAS_DETALLADAS.get("producto", PREGUNTAS["producto"])
        return PREGUNTAS["producto"]

    variables_faltantes = clasificacion.get("variables_faltantes", [])

    if not variables_faltantes:
        return PREGUNTAS["producto"]

    primera_variable = variables_faltantes[0]

    # Si la query es larga, es una concatenación — usar versión detallada
    if len(query) > 60:
        return PREGUNTAS_DETALLADAS.get(primera_variable, PREGUNTAS.get(primera_variable, PREGUNTAS["producto"]))

    return PREGUNTAS.get(primera_variable, PREGUNTAS["producto"])
