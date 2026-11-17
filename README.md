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

