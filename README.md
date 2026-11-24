# Recomendador educativo y plugin Moodle

El uso principal es el bloque de Moodle. No necesitas abrir un buscador en la
computadora para generar el instalable. Desde la rama `codex/motor-hibrido`:

```bash
git pull --ff-only origin codex/motor-hibrido
python3 scripts/package_plugin.py
```

Sube `block_videorec.zip` a Moodle y actualiza también el proyecto Python del
servidor. [Guía de configuración y actualización v0.4.0](docs/06_PLUGIN_MOODLE.md).

## Prototipo local opcional — E5

Implementado en el motor Python y el buscador local: análisis semántico → filtro
por umbral → filtrado colaborativo por vecinos → combinación y ranking final.
El enriquecimiento de metadatos queda pendiente.

```bash
python3 -m recomendador --web
```

El buscador inicia en YouTube real con Híbrido (contenido + colaborativo).
Escribe tu identificador local para guardar valoraciones. Sin historial suficiente
se conserva la puntuación semántica. No se cargan valoraciones simuladas por defecto.

[Funcionamiento, consola y límites de E5](docs/07_MOTOR_HIBRIDO.md).

El modo antiguo de consola `hibrido` sigue siendo textual + semántico;
el método nuevo se llama `hibrido_colaborativo`.

## Plugin Moodle v0.4.0 — conexión mediante exec()

El bloque utiliza el motor Python de este proyecto para buscar videos reales de YouTube.
El botón Recomendar ejecuta análisis semántico, filtro y ranking híbrido colaborativo.
Las valoraciones se guardan por usuario y curso en Moodle; la cuenta procede de la
sesión, sin escribir identificadores manualmente. Sin historial suficiente, el
resultado utiliza contenido semántico. No necesita abrir el servidor web local.

Para generar el ZIP instalable desde Antigravity:

```bash
python3 scripts/package_plugin.py
```

El resultado es `block_videorec.zip`. Se actualiza también el código Python del
servidor: el ZIP del plugin no incorpora modelos ni dependencias Python.

- Instalable: **block_videorec.zip**, con carpeta raíz videorec/.
- [Instalación, configuración y comprobaciones](docs/06_PLUGIN_MOODLE.md).
- Fuente del plugin: moodle_plugin/videorec/.
- Entrada Python ejecutada por PHP: moodle_bridge.py.
- Pruebas: python3 -m unittest discover tests -v.

Los modelos y las dependencias se instalan en el servidor Python, fuera del ZIP.
La instalación completa en Moodle y la validación de recomendaciones con docentes
siguen pendientes. Las pruebas de código incluyen mocks y ejecución real PHP/Python
con catálogo y embeddings de prueba, sin consultar YouTube en esta revisión.

---

## Documentación anterior del prototipo E1/E2

# Recomendador_ext – Prototipo E1 / E2

Recomendador de videos educativos – etapas E1 (catálogo simulado y coincidencia textual) y E2 (recuperación de candidatos reales mediante YouTube Data API v3).

## Requisitos

- Python 3.10 o superior (probado con Python 3.14.6).
- Solo biblioteca estándar de Python (no requiere instalar dependencias externas).
- Clave de YouTube Data API v3 configurada en `YOUTUBE_API_KEY` o en archivo `.env` (requerida para `--fuente youtube`).

## Estructura

```
Recomendador_ext/
├── AGENTS.md                  # Instrucciones del proyecto
├── README.md                  # Este archivo
├── data/
│   └── videos_demo.json       # Catálogo simulado (10 registros ficticios)
├── docs/                      # Documentación y seguimiento del proyecto
├── moodle_plugin/             # Estructura del plugin para Moodle (bloque PHP)
├── recomendador/
│   ├── __init__.py            # Paquete del recomendador
│   ├── __main__.py            # Entrada de consola (CLI)
│   ├── catalogo.py            # Lectura y validación del catálogo simulado
│   ├── ranking.py             # Motor de coincidencia textual y ranking
│   └── youtube.py             # Cliente de YouTube Data API v3 y manejo de errores
└── tests/
    ├── __init__.py
    ├── test_ranking.py        # 23 pruebas unitarias de catálogo y ranking
    └── test_youtube.py        # 12 pruebas unitarias de YouTube API (mocks, cuotas y errores)
```

## Ejecución

Desde la raíz del proyecto:

### 1. Búsqueda con catálogo simulado (E1)

```bash
# Búsqueda básica
python3 -m recomendador --tema "bases de datos"

# Con límite de resultados (1 a 5)
python3 -m recomendador --tema "programación" --limite 3
```

### 2. Búsqueda con candidatos reales de YouTube (E2)

```bash
# Búsqueda en YouTube Data API v3 (salida JSON)
python3 -m recomendador --tema "programacion python" --fuente youtube --limite 3

# Ajustando el número de candidatos a recuperar previamente (ej. 15 candidatos)
python3 -m recomendador --tema "machine learning" --fuente youtube --max-candidatos 15 --limite 5
```

### 3. Visualización gráfica fuera de Moodle (Navegador)

Dispones de dos formas para ver las tarjetas de video y reproducirlos en tu navegador:

#### A. Exportar consulta a vista HTML interactiva:
```bash
# Ejecuta la recomendación y abre automáticamente 'recomendaciones.html' en tu navegador:
python3 -m recomendador --tema "bases de datos relacionales" --fuente youtube --html
```

#### B. Explorador web interactivo en vivo:
```bash
# Inicia un servidor web local (http://127.0.0.1:8080) con buscador visual:
python3 -m recomendador --web
```
Permite buscar temas en vivo, alternar entre YouTube y el catálogo simulado, ver las miniaturas y reproducir los videos en un modal sin salir de la página.


### Ejemplo de salida (YouTube - E2)

```json
{
  "metodo": "coincidencia_textual",
  "datos": "youtube",
  "consulta": "programacion python",
  "terminos_utilizados": [
    "programacion",
    "python"
  ],
  "resultados": [
    {
      "id": "Rv910T1BJUw",
      "titulo": "¿Sabes qué es PYTHON y por qué es un lenguaje de programación tan importante?",
      "puntuacion": 1.0,
      "coincidencias": [
        "programacion",
        "python"
      ],
      "url": "https://www.youtube.com/watch?v=Rv910T1BJUw",
      "canal": "Computer Hoy",
      "origen": "youtube"
    }
  ]
}
```

## Pruebas

Ejecutar la suite completa de 35 pruebas unitarias:

```bash
python3 -m unittest discover tests -v
```

O por módulo específico:
```bash
python3 -m unittest tests.test_ranking -v
python3 -m unittest tests.test_youtube -v
```

Las pruebas cubren:
- Normalización, acentos y palabras funcionales.
- Puntuación, empates y límites de resultados.
- Catálogo ausente, corrupto o incompleto.
- Mocks de YouTube Data API: respuestas exitosas, respuestas vacías, cuota excedida (`quotaExceeded`), peticiones inválidas (400), errores de red y tiempos de espera agotados.
- Lectura segura de claves de API desde `.env` y variables de entorno.

## Notas

- **Credenciales**: las claves de API no se exponen en repositorios ni salidas; se leen desde el entorno local o `.env`.
- **Método**: coincidencia textual directa. Es una línea base algorítmica; las siguientes etapas incorporarán análisis semántico y filtrado colaborativo.
- **Siguiente etapa**: E3 incorporará análisis semántico de transcripciones o descripciones enriquecidas.


