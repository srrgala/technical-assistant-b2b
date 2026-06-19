# main.py — Orquestación del flujo completo. Sin lógica propia.

import os
from dotenv import load_dotenv
load_dotenv()
from core.classifier import clasificar, FUERA_DE_ALCANCE, INCOMPLETA, COMPLETA, COMPARACION
from core.clarifier import generar_pregunta
from core.retriever import recuperar
from core.responder import construir_respuesta
from core.identity import detectar_tipo, responder as responder_identidad
from core import fallback
from config import PRODUCTOS_VALIDOS, KB_DIR


def _cargar_kb_completa(producto_id: str) -> str | None:
    """Carga el archivo KB completo de un producto."""
    datos = PRODUCTOS_VALIDOS.get(producto_id)
    if not datos:
        return None
    ruta = os.path.join(KB_DIR, datos["archivo_kb"])
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def procesar_consulta(query: str) -> dict:
    """
    Punto de entrada principal del sistema.
    Recibe la query tal como llega (original o concatenada por el cliente).
    Devuelve siempre un dict con claves 'respuesta' y 'requiere_clarificacion'.
    """

    # 0. Saludos e identidad → respuesta directa sin pasar por classifier
    tipo_identidad = detectar_tipo(query)
    if tipo_identidad:
        return {"respuesta": responder_identidad(tipo_identidad), "requiere_clarificacion": False}

    # 1. Clasificar la consulta
    clasificacion = clasificar(query)
    tipo = clasificacion["tipo"]

    # 2. Fuera de alcance → fallback según motivo
    if tipo == FUERA_DE_ALCANCE:
        if clasificacion.get("motivo") == "recomendacion_catalogo":
            return {"respuesta": fallback.fuera_de_alcance_recomendacion(), "requiere_clarificacion": False}
        return {"respuesta": fallback.fuera_de_alcance(), "requiere_clarificacion": False}

    # 3. Incompleta → una sola pregunta de clarificación
    if tipo == INCOMPLETA:
        return {"respuesta": generar_pregunta(clasificacion), "requiere_clarificacion": True}

    # 4. Comparación → cargar KB completa de ambos productos y comparar
    if tipo == COMPARACION:
        productos_ids = clasificacion["productos_ids"]
        contextos = []
        for pid in productos_ids:
            kb = _cargar_kb_completa(pid)
            if kb:
                nombre = PRODUCTOS_VALIDOS[pid]["nombre_completo"]
                contextos.append(f"=== {nombre} ===\n{kb}")
        if not contextos:
            return {"respuesta": fallback.sin_informacion(), "requiere_clarificacion": False}
        contexto_combinado = "\n\n".join(contextos)
        return construir_respuesta(query, productos_ids[0], contexto_combinado)

    # 5. Completa → recuperar contexto y construir respuesta
    producto_id = clasificacion["producto_id"]
    contexto = recuperar(query, producto_id)

    return construir_respuesta(query, producto_id, contexto)


# --- Punto de entrada para pruebas en CLI ---
if __name__ == "__main__":
    print("Asistente técnico Llana — MVP")
    print("Escribe 'salir' para terminar.\n")

    query_pendiente = None

    while True:
        query = input("Consulta: ").strip()
        if query.lower() == "salir":
            break
        if not query:
            continue

        if query_pendiente:
            query = f"{query_pendiente} {query}"
            query_pendiente = None

        resultado = procesar_consulta(query)

        if resultado["requiere_clarificacion"]:
            query_pendiente = query

        print(f"\nAsistente: {resultado['respuesta']}\n")
