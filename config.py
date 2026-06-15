# config.py — Fuente única de verdad para alcance y constantes del sistema

MARCA = "Llana"

PRODUCTOS_VALIDOS = {
    "juncta_epox_rg2": {
        "nombre_completo": "Juncta Epox RG-2",
        "aliases": [
            "juncta epox", "epox rg-2", "rg-2", "juncta rg",
            "junta epóxica", "junta epoxi", "mortero epóxico",
            "epoxi piscina", "junta piscina", "rejuntar piscina",
            "agua salada", "junta salada",
        ],
        "categoria": "morteros_juntas",
        "archivo_kb": "JunctaEpoxRG2.txt",
        "variables_criticas": {
            "entorno": [
                "piscina", "exterior", "interior", "humedad", "agua", "mojado",
                "agua salada", "salada", "salado", "quimico", "químico",
                "intemperie", "fachada", "terraza", "cubierta", "bañera", "ducha",
            ],
        },
    },
    "juncta_mineral_cg2wa": {
        "nombre_completo": "Juncta Mineral CG2-WA",
        "aliases": [
            "juncta mineral", "cg2-wa", "cg2 wa", "cg2", "juncta cg2",
            "mineral cg2", "mortero junta mineral",
        ],
        "categoria": "morteros_juntas",
        "archivo_kb": "JunctaMineralCG2WA.txt",
        "variables_criticas": {
            "entorno": [
                "exterior", "interior", "piscina", "humedad", "agua", "mojado",
                "fachada", "terraza", "zona húmeda", "cubierta",
            ],
        },
    },
    "tixar_flex_duo_s2": {
        "nombre_completo": "Tixar Flex Duo S2",
        "aliases": [
            "tixar flex", "tixar duo", "flex duo", "tixar s2",
            "adhesivo s2", "gran formato", "doble encolado",
            "suelo radiante", "máxima deformabilidad", "maxima deformabilidad",
            "alta deformabilidad", "deformabilidad s2", "bicomponente",
        ],
        "categoria": "adhesivos",
        "archivo_kb": "TixarFlexDuoS2.txt",
        "variables_criticas": {
            "soporte": [
                "porcelanico", "porcelánico", "gres", "ceramica", "cerámica",
                "piedra", "marmol", "mármol", "baldosa", "piezas", "gran formato",
                "formato", "hormigon", "hormigón", "madera", "metal",
                "soporte", "superficie", "pared", "suelo", "pavimento",
                "interior", "exterior", "fachada", "terraza",
            ],
            "entorno": [
                "exterior", "interior", "fachada", "terraza",
                "suelo radiante", "radiante", "calefacción", "calefaccion",
                "piscina", "humedad", "agua", "mojado",
            ],
        },
    },
    "tixar_gel_mono_s1": {
        "nombre_completo": "Tixar Gel Mono S1",
        "aliases": [
            "tixar gel", "gel mono", "tixar mono", "tixar s1",
            "adhesivo s1", "monocomponente", "gel antideslizante",
        ],
        "categoria": "adhesivos",
        "archivo_kb": "TixarGelMonoS1.txt",
        "variables_criticas": {
            "soporte": [
                "porcelanico", "porcelánico", "gres", "ceramica", "cerámica",
                "piedra", "marmol", "mármol", "baldosa",
                "hormigon", "hormigón", "madera", "yeso",
                "soporte", "superficie", "pared", "suelo", "pavimento",
                "interior", "exterior", "fachada", "terraza",
            ],
            "entorno": [
                "exterior", "interior", "fachada", "terraza",
                "piscina", "humedad", "agua", "mojado", "vertical",
            ],
        },
    },
    "cobertec_vial_ligero": {
        "nombre_completo": "Cobertec Vial Ligero",
        "aliases": [
            "cobertec vial", "vial ligero", "cobertec garaje",
            "garaje", "garaje privado", "parking privado",
            "tráfico ligero", "trafico ligero",
        ],
        "categoria": "sistemas_constructivos",
        "archivo_kb": "CobertecVialLigero.txt",
        "variables_criticas": {
            "uso": [
                "garaje", "garage", "parking", "rampa", "nave",
                "almacen", "almacén", "planta", "suelo", "pavimento",
                "pasillo", "corredor", "zona de paso", "acceso",
            ],
        },
    },
    "cobertec_pool": {
        "nombre_completo": "Cobertec Pool",
        "aliases": [
            "cobertec pool", "pool", "impermeabilizar piscina",
            "vaso piscina", "vaso de piscina", "vaso",
            "alicatar", "lámina piscina",
        ],
        "categoria": "sistemas_constructivos",
        "archivo_kb": "CobertecPool.txt",
        "variables_criticas": {
            "entorno": [
                "piscina", "vaso", "inmersión", "inmersion", "agua",
                "lámina", "lamina", "deposito", "depósito", "estanque",
                "alicatar", "azulejo", "baldosa", "ceramica",
            ],
        },
    },
}

CATEGORIAS_VALIDAS = ["adhesivos", "morteros_juntas", "sistemas_constructivos"]

KEYWORDS_DOMINIO = [
    # Materiales
    "adhesivo", "mortero", "junta", "baldosa", "azulejo",
    "porcelanico", "porcelánico", "gres", "cerámica", "ceramica",
    "travertino", "piedra", "mármol", "marmol",
    # Acciones
    "aplicar", "pegar", "nivelar", "mezclar", "rejuntar",
    "impermeabilizar", "alicatar", "revestir",
    # Condiciones técnicas
    "exterior", "interior", "humedad", "secado", "fraguado", "deformabilidad",
    # Localización / contexto
    "superficie", "soporte", "piscina", "garaje", "parking", "pavimento",
    "fachada", "gran formato",
    # Intención de consulta de producto
    "producto", "recomiend",
    # Marca y gama
    "juncta", "tixar", "cobertec", "llana",
    # Nomenclatura normativa
    "cg2", "rg-2",
]

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

KEYWORDS_INTENCION_TECNICA = [
    "sirve", "es adecuado",
    "puedo usar", "puedo aplicar",
    "cómo usar", "como usar", "cómo uso", "como uso",
    "cómo aplicar", "como aplicar", "cómo aplico", "como aplico",
    "aplicación", "aplicacion",
    "es compatible", "vale para",
    "recomendación", "recomendacion", "qué usar", "que usar",
]

KB_DIR = "kb"
