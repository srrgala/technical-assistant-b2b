import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.classifier import clasificar, FUERA_DE_ALCANCE, INCOMPLETA, COMPLETA
from core.clarifier import generar_pregunta
from core import fallback
from main import procesar_consulta

# ---------------------------------------------------------------------------
# Tests de classifier
# ---------------------------------------------------------------------------

def test_fuera_de_alcance_consulta_generica():
    r = clasificar("¿Cuál es la capital de Francia?")
    assert r["tipo"] == FUERA_DE_ALCANCE, f"Esperado fuera_de_alcance, obtenido: {r['tipo']}"
    print("✓ test_fuera_de_alcance_consulta_generica")


def test_fuera_de_alcance_tiempo_meteorologico():
    r = clasificar("¿Qué tiempo hace mañana?")
    assert r["tipo"] == FUERA_DE_ALCANCE, f"Esperado fuera_de_alcance, obtenido: {r['tipo']}"
    print("✓ test_fuera_de_alcance_tiempo_meteorologico")


def test_fuera_de_alcance_anclajes_fuera_catalogo():
    r = clasificar("¿Tenéis algo para anclajes químicos de varillas roscadas?")
    assert r["tipo"] == FUERA_DE_ALCANCE, f"Esperado fuera_de_alcance, obtenido: {r['tipo']}"
    print("✓ test_fuera_de_alcance_anclajes_fuera_catalogo")


def test_incompleta_sin_producto():
    r = clasificar("¿Qué adhesivo uso para exterior?")
    assert r["tipo"] == INCOMPLETA, f"Esperado incompleta, obtenido: {r['tipo']}"
    assert r["producto_id"] is None
    print("✓ test_incompleta_sin_producto")


def test_incompleta_sin_producto_pregunta_generica():
    r = clasificar("¿qué producto me recomiendas?")
    assert r["tipo"] == INCOMPLETA, f"Esperado incompleta, obtenido: {r['tipo']}"
    assert r["producto_id"] is None
    print("✓ test_incompleta_sin_producto_pregunta_generica")


def test_incompleta_con_producto_sin_contexto():
    r = clasificar("Tengo el Tixar Flex")
    assert r["tipo"] == INCOMPLETA, f"Esperado incompleta, obtenido: {r['tipo']}"
    assert r["producto_id"] == "tixar_flex_duo_s2"
    print("✓ test_incompleta_con_producto_sin_contexto")


def test_completa_tixar_flex_con_contexto():
    r = clasificar("¿El gran formato sirve para fachada exterior sobre hormigón?")
    assert r["tipo"] == COMPLETA, f"Esperado completa, obtenido: {r['tipo']}"
    assert r["producto_id"] == "tixar_flex_duo_s2"
    print("✓ test_completa_tixar_flex_con_contexto")


def test_completa_juncta_epox_piscina():
    r = clasificar("rejuntar piscina de agua salada, junta 8 mm")
    assert r["tipo"] == COMPLETA, f"Esperado completa, obtenido: {r['tipo']}"
    assert r["producto_id"] == "juncta_epox_rg2"
    print("✓ test_completa_juncta_epox_piscina")


def test_completa_cobertec_vial_garaje():
    r = clasificar("impermeabilizar suelo de garaje privado")
    assert r["tipo"] == COMPLETA, f"Esperado completa, obtenido: {r['tipo']}"
    assert r["producto_id"] == "cobertec_vial_ligero"
    print("✓ test_completa_cobertec_vial_garaje")


def test_completa_cobertec_pool_piscina():
    r = clasificar("impermeabilizar el vaso de una piscina antes de alicatar")
    assert r["tipo"] == COMPLETA, f"Esperado completa, obtenido: {r['tipo']}"
    assert r["producto_id"] == "cobertec_pool"
    print("✓ test_completa_cobertec_pool_piscina")


def test_discriminacion_s2_vs_s1():
    """S2 se detecta por máxima deformabilidad; S1 NO debe aparecer en query con S2."""
    r = clasificar("adhesivo para suelo radiante con piezas de gran formato, necesito máxima deformabilidad")
    assert r["tipo"] == COMPLETA, f"Esperado completa, obtenido: {r['tipo']}"
    assert r["producto_id"] == "tixar_flex_duo_s2", f"Esperado tixar_flex_duo_s2, obtenido: {r['producto_id']}"
    assert r["producto_id"] != "tixar_gel_mono_s1", "No debe clasificar como S1"
    print("✓ test_discriminacion_s2_vs_s1")


# ---------------------------------------------------------------------------
# Tests de clarifier
# ---------------------------------------------------------------------------

def test_clarifier_sin_producto():
    clasificacion = {
        "tipo": INCOMPLETA,
        "producto_id": None,
        "razon": "test",
        "variables_faltantes": [],
        "query_original": "¿qué producto me recomiendas?",
    }
    pregunta = generar_pregunta(clasificacion)
    assert "?" in pregunta
    assert len(pregunta) > 10
    print("✓ test_clarifier_sin_producto")


def test_clarifier_con_producto_faltante_entorno():
    clasificacion = {
        "tipo": INCOMPLETA,
        "producto_id": "tixar_flex_duo_s2",
        "razon": "test",
        "variables_faltantes": ["entorno"],
        "query_original": "Tengo el Tixar Flex",
    }
    pregunta = generar_pregunta(clasificacion)
    assert "?" in pregunta
    print("✓ test_clarifier_con_producto_faltante_entorno")


# ---------------------------------------------------------------------------
# Tests de flujo completo
# ---------------------------------------------------------------------------

def test_flujo_fuera_de_alcance():
    r = procesar_consulta("¿Cuánto cuesta el metro cuadrado en Madrid?")
    assert r == fallback.fuera_de_alcance()
    print("✓ test_flujo_fuera_de_alcance")


def test_flujo_off_topic_tiempo():
    r = procesar_consulta("¿Qué tiempo hace mañana?")
    assert r == fallback.fuera_de_alcance()
    print("✓ test_flujo_off_topic_tiempo")


def test_flujo_incompleta_devuelve_pregunta():
    r = procesar_consulta("¿qué producto me recomiendas?")
    assert r != fallback.fuera_de_alcance()
    assert r != fallback.sin_informacion()
    assert "?" in r
    print("✓ test_flujo_incompleta_devuelve_pregunta")


def test_flujo_anclajes_fuera_catalogo():
    r = procesar_consulta("¿Tenéis algo para anclajes químicos de varillas roscadas?")
    # Debe ser fallback — no forzar coincidencia con ningún producto del catálogo
    assert r == fallback.fuera_de_alcance()
    print("✓ test_flujo_anclajes_fuera_catalogo")


if __name__ == "__main__":
    print("=== Test de comportamiento — Asistente Técnico Llana ===\n")

    # Classifier
    test_fuera_de_alcance_consulta_generica()
    test_fuera_de_alcance_tiempo_meteorologico()
    test_fuera_de_alcance_anclajes_fuera_catalogo()
    test_incompleta_sin_producto()
    test_incompleta_sin_producto_pregunta_generica()
    test_incompleta_con_producto_sin_contexto()
    test_completa_tixar_flex_con_contexto()
    test_completa_juncta_epox_piscina()
    test_completa_cobertec_vial_garaje()
    test_completa_cobertec_pool_piscina()
    test_discriminacion_s2_vs_s1()

    # Clarifier
    test_clarifier_sin_producto()
    test_clarifier_con_producto_faltante_entorno()

    # Flujo completo
    test_flujo_fuera_de_alcance()
    test_flujo_off_topic_tiempo()
    test_flujo_incompleta_devuelve_pregunta()
    test_flujo_anclajes_fuera_catalogo()

    print("\n=== Todos los tests pasaron ===")
