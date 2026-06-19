# Technical Assistant B2B

**Asistente técnico conversacional para distribuidores e instaladores de materiales de construcción.**

Proyecto \#3 del portfolio técnico — perfil híbrido Marketing \+ IA aplicada a B2B.

---

## Problema de negocio

Los distribuidores e instaladores de materiales de construcción reciben a diario consultas técnicas repetitivas: compatibilidades de producto, especificaciones por uso, dosificaciones, sistemas constructivos. Ese volumen lo absorbe personal técnico con tiempo y coste reales, o se deriva a manuales que nadie lee.

Este sistema actúa como primer punto de contacto técnico: interpreta la consulta en lenguaje natural, la contrasta contra la base de conocimiento del fabricante, pide clarificación cuando la consulta es ambigua y responde con precisión de catálogo. El técnico humano interviene solo cuando el caso lo requiere.

---

## Arquitectura

flowchart TD

    A(\[Consulta del usuario\]) \--\> B{identity.py\\nSaludo / identidad}

    B \--\>|Sí| C(\[Respuesta de identidad\])

    B \--\>|No| D{classifier.py\\nDeterminista}

    D \--\>|fuera\_de\_alcance| E(\[Fallback de dominio\])

    D \--\>|incompleta| F\[clarifier.py\\nPregunta de seguimiento\]

    F \--\> G(\[Usuario aclara\])

    G \--\> A

    D \--\>|comparacion| H\[retriever.py\\nCarga KB de ambos productos\]

    D \--\>|completa| I\[retriever.py\\nKeyword matching sobre KB\]

    H \--\> J\[responder.py\\nLLM — claude-sonnet-4-6\]

    I \--\> J

    J \--\> K(\[Respuesta técnica\])

---

## Decisiones técnicas

### RAG sobre prompt estático

La alternativa al RAG era incluir toda la KB en el system prompt. Eso funciona para catálogos pequeños, pero escala mal: cada consulta carga el catálogo completo en contexto, el coste por token crece linealmente con el tamaño de la KB, y la precisión baja porque el modelo tiene que encontrar el dato relevante en mucho ruido.

Con RAG, cada consulta recupera solo los fragmentos relevantes. El contexto que llega al LLM es pequeño y pertinente. La KB puede crecer sin impactar el coste ni la latencia de forma significativa.

### Retrieval por keyword matching, no por embeddings

El retriever no usa embeddings vectoriales ni índice semántico. Extrae los términos significativos de la query (eliminando stopwords), localiza los párrafos del archivo de KB que los contienen y pasa solo esos fragmentos al LLM. Si no hay match, pasa el documento completo como fallback.

Esta elección tiene un coste — no detecta sinónimos ni variantes morfológicas que no aparezcan en la KB — pero elimina dependencias de infraestructura vectorial (sin servidor de embeddings, sin índice que mantener) y es suficiente para un catálogo técnico con terminología normalizada como el de construcción.

### KB multi-marca como decisión de dominio

Un distribuidor real no maneja una sola línea de producto. Maneja varias marcas del mismo fabricante con catálogos solapados, y el técnico necesita saber qué producto de qué línea aplica a cada caso — incluyendo cuándo dos productos son compatibles entre sí.

La KB cubre tres marcas ficticias (Juncta, Tixar, Cobertec) bajo el mismo fabricante. Esa estructura replica el caso de uso real y obliga al sistema a resolver consultas que cruzan marcas, no solo consultas sobre un producto aislado. El sistema detecta explícitamente consultas de comparación entre dos productos y carga las KB de ambos antes de responder.

### KB sintética como decisión deliberada

La base de conocimiento usa productos ficticios, no un catálogo real de proveedor. Esa decisión tiene dos razones. Primera, legal: una KB real conlleva implicaciones de confidencialidad que no corresponden a un proyecto de portfolio. Segunda, técnica: una KB sintética bien construida demuestra que el sistema funciona con el tipo de dato correcto — fichas técnicas reales de construcción, con su terminología y estructura — no con un corpus genérico.

### Classifier determinista antes del LLM

Consultas fuera del dominio de construcción, preguntas sobre precio o disponibilidad, y comparaciones entre productos se resuelven con lógica determinista antes de llegar al retriever. Reduce llamadas innecesarias a la API y hace el sistema más predecible en los límites. Saludos y preguntas de identidad tienen su propia capa anterior al classifier.

### Clarificación como comportamiento de primer nivel

Cuando la consulta es ambigua — "¿qué adhesivo uso?" sin especificar soporte, condiciones o formato — el sistema no adivina ni da una respuesta genérica. Pide la información que necesita. Eso es más útil para el usuario y más honesto sobre los límites del sistema.

---

## Stack

| Capa | Tecnología |
| :---- | :---- |
| Backend | FastAPI \+ Python |
| LLM | Claude Sonnet (`claude-sonnet-4-6`) |
| Retrieval | Keyword matching sobre archivos de KB |
| Frontend | HTML / CSS / JS vanilla |
| Servidor | Uvicorn |
| Deploy | Render (Web Service) |
| VCS | GitHub |

---

## Estructura del proyecto

technical-assistant-b2b/

├── api.py                   \# FastAPI app \+ endpoints

├── main.py                  \# Orquestador del flujo completo

├── config.py                \# Productos válidos, aliases, keywords de dominio

├── core/

│   ├── \_\_init\_\_.py

│   ├── classifier.py        \# Classifier determinista

│   ├── clarifier.py         \# Generación de preguntas de clarificación

│   ├── retriever.py         \# Keyword matching sobre KB

│   ├── responder.py         \# Construcción de respuesta vía LLM

│   ├── fallback.py          \# Textos de fallback

│   └── identity.py          \# Saludos y preguntas de identidad

├── kb/

│   ├── CobertecPool.txt

│   ├── CobertecVialLigero.txt

│   ├── JunctaEpoxRG2.txt

│   ├── JunctaMineralCG2WA.txt

│   ├── TixarFlexDuoS2.txt

│   └── TixarGelMonoS1.txt

├── prompts/

│   └── system\_prompt.txt

├── tests/

│   ├── smoke\_matrix.py      \# Smoke tests de comportamiento end-to-end

│   └── test\_comportamiento.py

├── index.html               \# Frontend completo (servido por api.py)

├── requirements.txt

├── .env.example

└── .gitignore

---

## Instalación local

git clone https://github.com/srrgala/llana-rag

cd technical-assistant-b2b

python \-m venv venv

source venv/bin/activate        \# Windows: venv\\Scripts\\activate

pip install \-r requirements.txt

cp .env.example .env            \# añade tu ANTHROPIC\_API\_KEY

## Arranque local

uvicorn api:app \--reload

Abre `http://localhost:8000`. Frontend y backend servidos por el mismo proceso.

---

## Deploy en Render

1. Conecta el repo en [render.com](https://render.com) → New Web Service
2. Añade `ANTHROPIC_API_KEY` en el dashboard (Environment → Add variable)
3. Configura:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`
4. Deploy

**Nota:** el plan gratuito de Render duerme el servicio tras inactividad. El primer request tras un período sin uso puede tardar \~50 segundos en responder.

URL de producción: https://technical-assistant-b2b.onrender.com

---

## Endpoints

| Método | Ruta | Descripción |
| :---- | :---- | :---- |
| GET | `/` | Frontend |
| GET | `/health` | Estado del servicio |
| POST | `/consulta` | Procesar consulta técnica |

### POST /consulta

**Request:**

{

  "query": "¿Qué adhesivo uso para porcelánico en exterior con ciclos de hielo-deshielo?"

}

**Response:**

{

  "respuesta": "Para porcelánico en exterior con ciclos de hielo-deshielo, la opción adecuada es Tixar Flex Duo S2...",

  "requiere\_clarificacion": false

}

**Campos:**

| Campo | Tipo | Descripción |
| :---- | :---- | :---- |
| `respuesta` | string | Texto visible al usuario — siempre presente |
| `requiere_clarificacion` | boolean | `true` si la respuesta es una pregunta de clarificación y el cliente debe reenviar con contexto adicional |

**Flujo stateless para consultas con clarificación:**

Cuando `requiere_clarificacion` es `true`, el cliente concatena la query original con la respuesta del usuario y reenvía como una sola query:

query original: "¿qué adhesivo uso?"

pregunta del sistema: "¿Sobre qué tipo de soporte vas a aplicarlo?"

respuesta del usuario: "porcelánico de gran formato en fachada exterior"

→ reenviar: "¿qué adhesivo uso? porcelánico de gran formato en fachada exterior"

**Comportamientos validados en producción:**

| Tipo de consulta | Resultado |
| :---- | :---- |
| Consulta técnica completa | Respuesta técnica estructurada |
| Consulta ambigua | Pregunta de clarificación (`requiere_clarificacion: true`) |
| Comparación entre dos productos | Respuesta comparativa con KB de ambos |
| Consulta comercial (precio, stock, distribuidor) | Rechazo indicando el alcance del asistente |
| Consulta de recomendación de catálogo ("mejor producto") | Mensaje honesto que explica el límite y deja un siguiente paso útil |

---

## Tests

\# Tests de comportamiento (sin API key — mockean el LLM)

pytest tests/test\_comportamiento.py \-v

\# Smoke matrix end-to-end (requiere API key)

python tests/smoke\_matrix.py

La smoke matrix cubre 8 casos: consultas completas por categoría, discriminación S2 vs S1, detección de comparación, clarificación, fuera de alcance y un test de regresión de IP que verifica que ninguna respuesta filtre contenido del repo origen.

---

## Base de conocimiento

Tres marcas del mismo fabricante, seis productos, tres categorías:

| Marca | Producto | Categoría |
| :---- | :---- | :---- |
| Juncta | Epox RG-2 | Morteros de juntas |
| Juncta | Mineral CG2-WA | Morteros de juntas |
| Tixar | Flex Duo S2 | Adhesivos |
| Tixar | Gel Mono S1 | Adhesivos |
| Cobertec | Vial Ligero | Sistemas constructivos |
| Cobertec | Pool | Sistemas constructivos |

Cada ficha cubre: descripción, usos recomendados, usos contraindicados, especificaciones técnicas, dosificación, condiciones de aplicación y compatibilidades con otros productos del catálogo.

---

## Limitaciones conocidas

- **KB de seis productos.** El sistema demuestra el patrón RAG sobre un catálogo técnico real de construcción, no su amplitud. Escalar la KB no requiere cambios de arquitectura.  
- **Retrieval por keywords.** El sistema no detecta sinónimos ni variantes morfológicas que no aparezcan en los archivos de KB. Una consulta con terminología muy alejada de la ficha técnica puede no recuperar los fragmentos óptimos.  
- **Sin persistencia server-side.** El historial lo gestiona el cliente via concatenación de query. Conversaciones largas aumentan el tamaño del payload.  
- **Una pregunta de clarificación por turno.** Más natural en conversación, pero puede alargar la resolución de consultas con múltiples variables desconocidas.  
- **Dependencia de la API de Anthropic.** Sin conexión o con rate limits, el servicio no funciona. No hay fallback offline.
