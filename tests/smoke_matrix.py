"""
Smoke test matrix — Fase 5
Ejecutar desde /Users/albertogala/technical-assistant-b2b/
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import procesar_consulta
from core import fallback

# Patrones de IP a verificar (ninguno debe aparecer en respuestas)
IP_PATTERNS = ["pegoland", "morcemcolor", "morcem cover", "grupo puma"]

CASOS = [
    {
        "id": 1,
        "query": "rejuntar piscina de agua salada, junta 8 mm",
        "categoria_esperada": "morteros_juntas",
        "producto_esperado": "Juncta Epox RG-2",
        "comportamiento": "debe mencionar Juncta Epox RG-2 y contexto de piscina/agua salada",
    },
    {
        "id": 2,
        "query": "adhesivo porcelánico gran formato en fachada",
        "categoria_esperada": "adhesivos",
        "producto_esperado": "Tixar Flex Duo S2",
        "comportamiento": "debe mencionar Tixar Flex Duo S2 y doble encolado",
    },
    {
        "id": 3,
        "query": "adhesivo para suelo radiante con piezas de gran formato, necesito máxima deformabilidad",
        "categoria_esperada": "adhesivos",
        "producto_esperado": "Tixar Flex Duo S2",
        "comportamiento": "debe ser S2 (bicomponente), NO debe recomendar S1",
        "no_debe_contener": ["Tixar Gel Mono S1", "tixar gel", "mono s1"],
    },
    {
        "id": 4,
        "query": "impermeabilizar suelo de garaje privado",
        "categoria_esperada": "sistemas_constructivos",
        "producto_esperado": "Cobertec Vial Ligero",
        "comportamiento": "debe mencionar Cobertec Vial Ligero, no Cobertec Pool",
        "no_debe_contener": ["cobertec pool"],
    },
    {
        "id": 5,
        "query": "impermeabilizar el vaso de una piscina antes de alicatar",
        "categoria_esperada": "sistemas_constructivos",
        "producto_esperado": "Cobertec Pool",
        "comportamiento": "debe mencionar Cobertec Pool, no Cobertec Vial",
        "no_debe_contener": ["cobertec vial"],
    },
    {
        "id": 6,
        "query": "¿qué producto me recomiendas?",
        "categoria_esperada": "CLARIFIER",
        "producto_esperado": None,
        "comportamiento": "debe disparar pregunta de clarificación (empieza por '¿')",
        "es_clarificacion": True,
    },
    {
        "id": 7,
        "query": "¿qué tiempo hace mañana?",
        "categoria_esperada": "FUERA_DE_ALCANCE",
        "producto_esperado": None,
        "comportamiento": "debe devolver fallback fuera de alcance",
        "es_fallback": True,
    },
    {
        "id": 8,
        "query": "¿tenéis algo para anclajes químicos de varillas roscadas?",
        "categoria_esperada": "FUERA_DE_ALCANCE / fuera de catálogo",
        "producto_esperado": None,
        "comportamiento": "fallback honesto sin forzar coincidencia con productos del catálogo",
        "es_fallback": True,
        "no_debe_contener": ["juncta", "tixar", "cobertec"],
    },
]


def verificar_ip(texto: str) -> list[str]:
    """Devuelve lista de patrones IP encontrados en la respuesta."""
    texto_lower = texto.lower()
    return [p for p in IP_PATTERNS if p in texto_lower]


def run_smoke():
    print("=" * 65)
    print("SMOKE TEST MATRIX — Asistente Técnico Llana")
    print("=" * 65)
    print()

    resultados = []

    for caso in CASOS:
        print(f"─── Caso {caso['id']} ───────────────────────────────────────")
        print(f"Query: {caso['query']}")
        print(f"Esperado: {caso['comportamiento']}")

        respuesta = procesar_consulta(caso["query"])

        print(f"Respuesta: {respuesta[:200]}{'...' if len(respuesta) > 200 else ''}")

        # Verificaciones
        ok = True
        issues = []

        # Check: clarificación esperada
        if caso.get("es_clarificacion"):
            if not respuesta.startswith("¿"):
                issues.append("ERROR: se esperaba pregunta de clarificación (inicio '¿')")
                ok = False

        # Check: fallback esperado
        if caso.get("es_fallback"):
            if respuesta == fallback.fuera_de_alcance() or "alcance" in respuesta.lower() or "fuera" in respuesta.lower():
                pass  # OK
            else:
                issues.append("ERROR: se esperaba fallback de fuera de alcance")
                ok = False

        # Check: producto esperado mencionado
        if caso.get("producto_esperado"):
            if caso["producto_esperado"].lower() not in respuesta.lower():
                issues.append(f"ERROR: respuesta no menciona '{caso['producto_esperado']}'")
                ok = False

        # Check: términos que NO deben aparecer
        if caso.get("no_debe_contener"):
            for term in caso["no_debe_contener"]:
                if term.lower() in respuesta.lower():
                    issues.append(f"ERROR: respuesta contiene término prohibido '{term}'")
                    ok = False

        # Check: regresión IP
        ip_found = verificar_ip(respuesta)
        if ip_found:
            issues.append(f"⚠️  REGRESIÓN IP: patrones encontrados: {ip_found}")
            ok = False

        estado = "✅ PASA" if ok else "❌ FALLA"
        print(f"Estado: {estado}")
        if issues:
            for issue in issues:
                print(f"  {issue}")
        print()

        resultados.append({"caso": caso["id"], "ok": ok, "issues": issues})

    # Resumen
    print("=" * 65)
    pasados = sum(1 for r in resultados if r["ok"])
    total = len(resultados)
    print(f"RESULTADO FINAL: {pasados}/{total} casos PASAN")

    if pasados == total:
        print("✅ SMOKE MATRIX: PASA — todos los casos en verde + IP limpia")
    else:
        print("❌ SMOKE MATRIX: FALLA — revisar casos anteriores")

    return pasados == total


if __name__ == "__main__":
    success = run_smoke()
    sys.exit(0 if success else 1)
