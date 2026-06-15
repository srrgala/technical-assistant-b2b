# classifier.py — Clasifica consultas según las reglas del spec y config

from __future__ import annotations

from config import PRODUCTOS_VALIDOS, KEYWORDS_DOMINIO

FUERA_DE_ALCANCE = "fuera_de_alcance"
INCOMPLETA = "incompleta"
COMPLETA = "completa"
COMPARACION = "comparacion"

KEYWORDS_FUERA_DE_ALCANCE = [
    "precio", "coste", "costo", "cuánto cuesta", "cuanto cuesta",
    "cuánto vale", "cuanto vale", "presupuesto",
    "disponible", "disponibilidad", "stock", "hay stock",
    "comprar", "dónde comprar", "donde comprar", "distribuidor",
    "plazo", "plazo de entrega", "entrega", "envío", "envio",
    "descuento", "oferta", "promoción", "promocion",
    "ficha comercial", "hoja comercial", "catálogo", "catalogo",
    "certificado", "homologación", "homologacion",
    "más vendido", "mas vendido", "mejor producto", "más popular", "mas popular",
    "pinturas", "pintura", "aislante",
]

KEYWORDS_COMPARACION = [
    "diferencia", "diferencias", "comparar", "comparación", "comparacion",
    "mejor", "cuál es mejor", "cual es mejor", "cuál elegir", "cual elegir",
    "cuál", "cual", "vs", "versus", "o el", "o la", "entre",
    "material es mejor", "cuál recomiendas", "cual recomiendas",
    "qué diferencia", "que diferencia", "cuál uso", "cual uso",
    "cuál escojo", "cual escojo", "cuál me conviene", "cual me conviene",
]


def _normalizar(texto: str) -> str:
    return texto.lower().strip()


def _es_intencion_fuera_de_alcance(query: str) -> bool:
    query_norm = _normalizar(query)
    return any(kw in query_norm for kw in KEYWORDS_FUERA_DE_ALCANCE)


def _es_comparacion(query: str) -> bool:
    query_norm = _normalizar(query)
    return any(kw in query_norm for kw in KEYWORDS_COMPARACION)


def detectar_productos(query: str) -> list[str]:
    query_norm = _normalizar(query)
    matches = []
    for producto_id, datos in PRODUCTOS_VALIDOS.items():
        for alias in datos["aliases"]:
            if alias in query_norm:
                matches.append(producto_id)
                break
    return matches


def detectar_producto(query: str) -> str | None:
    matches = detectar_productos(query)
    if len(matches) == 1:
        return matches[0]
    return None


def _pertenece_al_dominio(query: str) -> bool:
    query_norm = _normalizar(query)
    return any(kw in query_norm for kw in KEYWORDS_DOMINIO)


def _variables_faltantes(query: str, producto_id: str) -> list[str]:
    query_norm = _normalizar(query)
    variables_criticas = PRODUCTOS_VALIDOS[producto_id].get("variables_criticas", {})
    faltantes = []
    for variable, keywords in variables_criticas.items():
        if not any(kw in query_norm for kw in keywords):
            faltantes.append(variable)
    return faltantes


def clasificar(query: str) -> dict:
    if _es_intencion_fuera_de_alcance(query):
        return {
            "tipo": FUERA_DE_ALCANCE,
            "producto_id": None,
            "productos_ids": [],
            "variables_faltantes": [],
            "query_original": query,
            "razon": "Intención fuera del alcance funcional.",
        }

    productos = detectar_productos(query)
    producto_id = productos[0] if len(productos) == 1 else None

    if len(productos) == 2 and _es_comparacion(query):
        return {
            "tipo": COMPARACION,
            "producto_id": None,
            "productos_ids": productos,
            "variables_faltantes": [],
            "query_original": query,
            "razon": f"Comparación entre {productos[0]} y {productos[1]}.",
        }

    if not _pertenece_al_dominio(query) and producto_id is None:
        return {
            "tipo": FUERA_DE_ALCANCE,
            "producto_id": None,
            "productos_ids": [],
            "variables_faltantes": [],
            "query_original": query,
            "razon": "La consulta no pertenece al dominio del asistente.",
        }

    if producto_id is None:
        return {
            "tipo": INCOMPLETA,
            "producto_id": None,
            "productos_ids": [],
            "variables_faltantes": [],
            "query_original": query,
            "razon": "Sin producto válido identificado.",
        }

    faltantes = _variables_faltantes(query, producto_id)

    if faltantes:
        return {
            "tipo": INCOMPLETA,
            "producto_id": producto_id,
            "productos_ids": [producto_id],
            "variables_faltantes": faltantes,
            "query_original": query,
            "razon": f"Variables críticas ausentes: {faltantes}",
        }

    return {
        "tipo": COMPLETA,
        "producto_id": producto_id,
        "productos_ids": [producto_id],
        "variables_faltantes": [],
        "query_original": query,
        "razon": "Consulta procesable.",
    }
