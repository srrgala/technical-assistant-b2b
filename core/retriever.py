# retriever.py — Retrieval determinista por keyword matching sobre archivos /kb/
# Prioridad: precisión > recall. Si hay ambigüedad → devuelve vacío.

from __future__ import annotations

import os
from config import PRODUCTOS_VALIDOS, KB_DIR


def _cargar_archivo(nombre_archivo: str) -> str | None:
    """Carga el contenido del archivo de kb del producto. Devuelve None si no existe."""
    ruta = os.path.join(KB_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def _extraer_fragmentos(contenido: str, keywords: list[str]) -> list[str]:
    """
    Devuelve los párrafos del documento que contienen al menos una keyword relevante.
    La unidad mínima de fragmento es el párrafo (bloques separados por línea vacía).
    """
    parrafos = contenido.split("\n\n")
    relevantes = []
    for parrafo in parrafos:
        parrafo_norm = parrafo.lower()
        if any(kw.lower() in parrafo_norm for kw in keywords):
            relevantes.append(parrafo.strip())
    return relevantes


def _extraer_keywords_query(query: str) -> list[str]:
    """
    Extrae términos significativos de la query para buscar en el documento.
    Elimina stopwords básicas en español.
    """
    stopwords = {
        "el", "la", "los", "las", "de", "del", "en", "con", "para",
        "por", "que", "se", "es", "un", "una", "y", "o", "a", "al",
        "lo", "le", "si", "no", "me", "mi", "su", "sus", "este", "esta",
        "qué", "cómo", "cuál", "cuándo", "dónde", "antes",
    }
    tokens = query.lower().split()
    return [t for t in tokens if t not in stopwords and len(t) > 2]


def recuperar(query: str, producto_id: str) -> str | None:
    """
    Recupera fragmentos relevantes del archivo de kb del producto identificado.

    Reglas:
    - Solo opera sobre el producto ya identificado por el classifier
    - Si el archivo no existe → None
    - Si no hay fragmentos relevantes → None
    - Si hay fragmentos → devuelve string concatenado de fragmentos
    - No opera sobre múltiples productos (la ambigüedad la resuelve el classifier)
    """
    datos_producto = PRODUCTOS_VALIDOS.get(producto_id)
    if not datos_producto:
        return None

    contenido = _cargar_archivo(datos_producto["archivo_kb"])
    if not contenido:
        return None

    keywords = _extraer_keywords_query(query)
    if not keywords:
        return None

    fragmentos = _extraer_fragmentos(contenido, keywords)

    if not fragmentos:
        # Fallback: devolver el documento completo si no hay match de keywords
        return contenido

    return "\n\n".join(fragmentos)
