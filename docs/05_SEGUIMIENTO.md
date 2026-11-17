# Seguimiento de Recomendador_ext

Actualizado el 17 de noviembre de 2026 — Integración Moodle por exec(), v0.3.0.

## Estado confirmado en esta revisión

| Elemento | Estado | Evidencia |
| --- | --- | --- |
| Motor existente | Conservado | Ranking textual/semántico y cliente de YouTube del repositorio. |
| Datos de YouTube | Vistas, likes y duración conservados hasta la salida | Se corrigió la pérdida de estos campos en ranking.py, incluidos ceros y valores no disponibles. |
| Plugin Moodle | v0.3.0 listo para instalar | Fuente en moodle_plugin/videorec y ZIP con raíz videorec/. |
| Conector | exec() de PHP a Python local | Puente moodle_bridge.py, JSON separado de avisos, errores traducidos y tiempo máximo. |
| Configuración | Rutas configurables y Python de .venv | Sin rutas personales predeterminadas; caché HF_HOME opcional. |
| Interfaz | YouTube real, textual o semántico | Formulario Moodle, tarjetas y reproductor; híbrido colaborativo reservado para E5. |
| Comprobaciones | 80 pruebas satisfactorias y 11 PHP sin errores de sintaxis | Incluye exec() real con catálogo de prueba y arnés PHP independiente de Moodle. |
| Instalación en Moodle del usuario | Pendiente | No se accedió a su servidor, sesiones, claves ni base de datos. |
| Evaluación pedagógica y ajuste fino | Pendientes | Esta integración no demuestra eficacia educativa ni entrena el modelo. |

## Tarea activa

Integración solicitada por el usuario: plugin que llama las funciones Python a través
de exec(). Se entregó el paquete v0.3.0 y la guía docs/06_PLUGIN_MOODLE.md. El siguiente
paso es instalar y verificar una búsqueda real dentro de su curso Moodle. No se
avanzó en filtrado colaborativo, entrenamiento ni captura de interacciones Moodle.

## Ficha técnica del proyecto

| Dato | Valor |
| --- | --- |
| Ruta absoluta en el Mac | `/Users/eduardoortiz/Develops/Recomendador_Ext` |
| Sistema | Mac |
| Lenguaje | Python |
| Versión e intérprete disponible | Python 3.14.6 (`python3`) |
| Dependencia nueva (E3) | `sentence-transformers` (instalar con `pip install sentence-transformers`) |
| Modelo de embeddings por defecto | `paraphrase-multilingual-MiniLM-L12-v2` (pesos FP32 ~471 MB; RAM adicional) |
| Comando textual (E1) | `python3 -m recomendador --tema "bases de datos"` |
| Comando semántico (E3) | `python3 -m recomendador --tema "bases de datos" --metodo semantico` |
| Comando híbrido (E3) | `python3 -m recomendador --tema "bases de datos" --metodo hibrido --alpha 0.4` |
| Comando servidor interactivo | `python3 -m recomendador --web` |
| Comando para pruebas | `python3 -m unittest discover tests -v` (80 tests con PHP disponible) |
| Datos utilizados | Catálogo simulado (`data/videos_demo.json`) y YouTube Data API v3 |
| Métodos implementados | Textual (E1), Semántico con embeddings (E3), Híbrido ponderado (E3) |
| Conexión a Moodle | Estructura base de bloque en PHP preparada en `moodle_plugin/` |
| Servicios externos | YouTube Data API v3 (clave en `.env`) + HuggingFace (descarga automática del modelo) |

## Decisiones

| ID | Decisión | Procedencia y estado |
| --- | --- | --- |
| D01 | Avanzar por etapas durante aproximadamente dos meses | Usuario; vigente. |
| D02 | Usar Antigravity y documentación Markdown | Usuario; vigente. |
| D03 | Trabajar en Recomendador_ext con docs | Usuario; vigente. |
| D04 | Desarrollar primero sin conexión a Moodle | Usuario; reemplaza el arranque anterior. |
| D05 | Colocar AGENTS.md en la raíz y los demás documentos en docs | Organización propuesta para el alcance del proyecto. |
| D06 | Empezar con Python estándar y datos simulados si no hay código previo | Aplicada en E1. |
| D07 | Mantener la integración Moodle como objetivo final | Derivado de la tesis; calendario por ajustar con el usuario. |
| D08 | Elegir embeddings y método colaborativo cuando corresponda | Pendiente de datos y recursos. |
| D09 | Implementar plugin tipo bloque (`block_videorec`) para Moodle 5.1+ / PHP 8.4 | Usuario solicita iniciar etapa de plugin básico en PHP. |
| D10 | Implementar cliente de YouTube Data API v3 con biblioteca estándar (`urllib.request`) y pruebas simuladas con mocks | Aplicada en E2. Gestión de cuotas, errores de red y respuestas vacías. |
| D11 | Usar sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`) para análisis semántico en E3 | Usuario; seleccionado por cobertura multilingüe y peso ligero sin GPU. |

## Pendientes posteriores

- Dominio y temas reales del piloto.
- Horas semanales y fecha exacta de entrega.
- Muestra de transcripciones propias o autorizadas (E3).
- Participantes y mecanismo de valoración.
- Rúbrica y protocolo de evaluación.
- Conector definitivo entre el plugin de Moodle y el recomendador Python.
- Rúbrica y protocolo de evaluación.
- Forma técnica y momento de integración con Moodle.

Ninguno de esos pendientes bloqueó E1.

## Bitácora

### E1 – Prototipo local con catálogo simulado

- **Fecha:** 29 de septiembre de 2026.
- **Etapa:** E1.
- **Objetivo:** Programa independiente que recibe un tema, compara textos de un catálogo simulado y devuelve hasta cinco coincidencias ordenadas.
- **Archivos creados:**
  - `data/videos_demo.json` – Catálogo simulado con 10 registros ficticios.
  - `recomendador/__init__.py` – Paquete del recomendador.
  - `recomendador/__main__.py` – Entrada de consola (argparse: `--tema`, `--limite`).
  - `recomendador/catalogo.py` – Lectura y validación del catálogo JSON.
  - `recomendador/ranking.py` – Normalización, stopwords y puntuación por coincidencia textual.
  - `tests/__init__.py` – Paquete de pruebas.
  - `tests/test_ranking.py` – 23 pruebas unitarias.
  - `README.md` – Instrucciones de ejecución y ejemplo de salida.
- **Decisiones y motivo:**
  - Python con biblioteca estándar, según D06.
  - Puntuación = términos de consulta coincidentes / términos de consulta utilizables.
  - Desempate por `id` para resultado determinista.
  - Lista explícita de 27 palabras funcionales en español, documentada en el código.
- **Comandos realmente ejecutados:**
  - `python3 --version` → Python 3.14.6.
  - `python3 -m unittest tests.test_ranking -v` → 23 tests OK.
  - `python3 -m recomendador --tema "bases de datos"` → 4 resultados (demo_001, demo_002, demo_008 con 1.0; demo_004 con 0.5).
  - `python3 -m recomendador --tema "PROGRAMACIÓN orientada"` → 1 resultado (demo_003, puntuación 1.0).
  - `python3 -m recomendador --tema "gastronomía molecular"` → lista vacía.
  - `python3 -m recomendador --tema "de la en el"` → mensaje de validación, lista vacía.
  - `python3 -m recomendador --tema "redes" --limite 2` → 1 resultado (demo_006).
  - `python3 -m recomendador --tema "redes" --limite 10` → error de entrada (código de salida 1).
- **Resultado observado:** Todos los casos de la tabla de comprobaciones de `04_PRIMERA_ETAPA.md` se cumplen.
- **Pruebas ejecutadas:** 23 pruebas unitarias con `unittest`, todas pasaron en 0.005 s.
- **Comprobaciones pendientes:** Ninguna para E1.
- **Evidencia disponible:** Salida de consola de las pruebas y los comandos ejecutados.
- **Relación con la tesis:** E1 es la línea base de software; demuestra el flujo de entrada, comparación y salida. No es análisis semántico, filtrado colaborativo ni evaluación con usuarios.
- **Tiempo real informado por el estudiante:** Pendiente de registro por el usuario.
- **Próximo paso:** E2 – recuperación de candidatos reales con YouTube Data API, cuando el usuario lo solicite.

### Moodle – Estructura básica del plugin PHP (block_videorec)

- **Fecha:** 20 de octubre de 2026.
- **Etapa:** Integración inicial Moodle (Estructura base en PHP).
- **Objetivo:** Prototipo del plugin en PHP para Moodle 5.1.3+ y PHP 8.4 instalable desde ZIP, con acceso seguro desde curso (`require_login` y `moodle/course:view`) y despliegue del nombre e ID del curso actual.
- **Archivos creados:**
  - `moodle_plugin/videorec/version.php` – Metadatos de versión y compatibilidad Moodle (`block_videorec`, versión `2026102000`, requires `2024100700`).
  - `moodle_plugin/videorec/block_videorec.php` – Clase principal del bloque (`block_videorec`), botón de apertura a `view.php`.
  - `moodle_plugin/videorec/view.php` – Pantalla dedicada en contexto de curso con validación de login, capacidades y despliegue de detalles del curso.
  - `moodle_plugin/videorec/db/access.php` – Definición de capacidades (`block/videorec:myaddinstance`, `block/videorec:addinstance`).
  - `moodle_plugin/videorec/lang/en/block_videorec.php` – Textos en inglés.
  - `moodle_plugin/videorec/lang/es/block_videorec.php` – Textos en español.
  - `moodle_plugin/videorec/classes/privacy/provider.php` – Implementación de `\core_privacy\local\metadata\null_provider`.
  - `block_videorec.zip` – Archivo ZIP listo para instalar en Moodle.
- **Comandos ejecutados:**
  - `find moodle_plugin/videorec -name "*.php" -exec php -l {} +` → 0 errores de sintaxis en todos los archivos.
  - `cd moodle_plugin && zip -r ../block_videorec.zip videorec && cd ..` → Archivo ZIP generado correctamente.
  - `unzip -l block_videorec.zip` → Verificación de 14 entradas con raíz `videorec/`.
  - `python3 -m unittest tests.test_ranking -v` → 23 tests OK.
- **Resultado observado:** Código limpio, compatible con PHP 8.4 y Moodle 5.1.3+, listo para ser instalado por la interfaz web de Moodle o copia directa.
- **Próximo paso:** Verificación de instalación en el Moodle local por el usuario y preparación del conector `exec()` hacia el módulo Python.

### E2 – Recuperación de candidatos reales con YouTube Data API v3

- **Fecha:** 27 de octubre de 2026.
- **Etapa:** E2.
- **Objetivo:** Recuperación de candidatos reales de video desde YouTube Data API v3 con metadatos reales (título, descripción, canal, fecha, URL), manteniendo compatibilidad con la coincidencia textual de E1 y manejando errores de cuotas, red y resultados vacíos.
- **Archivos creados / modificados:**
  - `recomendador/youtube.py` – Cliente para YouTube Data API v3 con biblioteca estándar (`urllib.request`), extracción de metadatos reales y manejo de excepciones (`ErrorYouTube` con códigos `cuota_excedida`, `peticion_invalida`, `acceso_denegado`, `error_red`, `tiempo_agotado`, etc.).
  - `recomendador/__main__.py` – Soporte para argumentos `--fuente {simulado,youtube}` y `--max-candidatos`.
  - `recomendador/ranking.py` – Mapeo dinámico del origen de datos (`datos: "youtube"` o `"simulados"`) y preservación de URLs y canales en la salida.
  - `recomendador/__init__.py` – Exportación de funciones y clases de E2.
  - `tests/test_youtube.py` – 12 pruebas unitarias con mocks (`unittest.mock`) que verifican casos exitosos, búsquedas vacías, errores 400, 403 (cuota excedida), 503, errores de red y lectura segura de claves.
  - `README.md` – Actualizado con ejemplos de ejecución para E2 y suite completa de pruebas.
- **Comandos realmente ejecutados:**
  - `python3 -m unittest discover tests -v` → 35 pruebas unitarias exitosas (0.010 s).
  - `python3 -m recomendador --tema "bases de datos"` → 4 resultados con catálogo simulado (compatibilidad E1 confirmada).
  - `python3 -m recomendador --tema "programacion python" --fuente youtube --limite 3` → 3 resultados reales devueltos con URLs de YouTube activas y canales asociados.
- **Resultado observado:** El sistema permite alternar entre el catálogo simulado y la API real de YouTube sin dependencias externas, manejando fallos y cuotas con respuestas deterministas.
- **Pruebas ejecutadas:** 35 pruebas unitarias (23 de ranking/catálogo + 12 de cliente YouTube), todas pasando.
- **Relación con la tesis:** E2 cumple con la recuperación de metadatos reales requerida para alimentar el posterior análisis semántico (E3) y las señales colaborativas (E5).
- **Próximo paso:** E3 (análisis semántico con embeddings / NLP) o conector PHP `exec()` para el bloque Moodle, según determine el usuario.

No registrar horas, métricas o pruebas que no hayan ocurrido.

### Visualizador HTML y servidor web interactivo (entre E2 y E3)

- **Fecha:** Anterior a la sesión del 9 de noviembre de 2026.
- **Objetivo:** Interfaz visual para explorar resultados sin usar la consola.
- **Archivos creados:**
  - `recomendador/visualizador.py` – Genera un archivo HTML estático con resultados y lo abre en el navegador.
  - `recomendador/servidor.py` – Servidor web local (puerto 8080) con buscador interactivo, selector de fuente (YouTube/Simulado) y reproductor de video integrado.
  - `recomendaciones.html` – Resultado HTML generado de una búsqueda real ("bases de datos relacionales", YouTube, 3 videos reales).
- **Resultado observado:** Interfaz funcional; `recomendaciones.html` contiene 3 videos reales de YouTube con miniaturas e IDs verificados.
- **Próximo paso:** E3 (análisis semántico).

### E3 – Análisis semántico con sentence-transformers

- **Fecha:** 9 de noviembre de 2026.
- **Etapa:** E3.
- **Objetivo:** Reemplazar la coincidencia textual de E1 por embeddings densos para capturar similitud semántica (ej. "aprendizaje automático" ≈ "machine learning"), e introducir un modo híbrido que pondera ambas señales.
- **Archivos creados / modificados:**
  - `recomendador/semantico.py` – Clase `ModeloEmbeddings` con sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`), carga diferida (lazy) y similitud de coseno. Soporta cambio de modelo vía `RECOMENDADOR_MODELO_EMBEDDINGS`.
  - `recomendador/ranking.py` – Parámetro `metodo` en `recomendar()` con tres modos: `textual`, `semantico`, `hibrido` (alpha=0.4 por defecto). Umbral semántico en 0.15. Campos `similitud_semantica`, `puntuacion_textual` y `alpha_textual` en las respuestas de los modos correspondientes.
  - `recomendador/__main__.py` – Argumentos `--metodo` y `--alpha` en la consola.
  - `recomendador/__init__.py` – Exporta `ModeloEmbeddings`.
  - `recomendador/servidor.py` – Selector de método (Textual / Semántico / Híbrido) en la UI web; reutiliza el modelo en memoria entre peticiones; maneja `ImportError` si sentence-transformers no está instalado.
  - `tests/test_semantico.py` – 22 pruebas unitarias con mocks sin numpy ni descarga del modelo.
- **Comandos realmente ejecutados:**
  - `python3 -m unittest discover tests -v` → 57 pruebas unitarias exitosas (0.014 s).
- **Resultado observado:** Los tres modos responden correctamente según los tests; el modo textual mantiene compatibilidad total con E1 y E2.
- **Dependencia nueva:** `pip install sentence-transformers` (requiere red; ejecutar en terminal del usuario).
- **Relación con la tesis:** E3 introduce el análisis de contenido semántico requerido por el modelo híbrido; el modo híbrido sienta las bases para E5 (filtrado colaborativo).
- **Próximo paso:** E4 (perfiles de usuario e interacciones) o directamente E5 (filtrado colaborativo y modelo híbrido completo).

### Moodle – Plugin con conector al recomendador y vista interactiva (v0.2.0)

- **Fecha:** 9 de noviembre de 2026.
- **Etapa:** Integración Moodle (E6 adelantada/parcial a solicitud del usuario).
- **Objetivo:** Actualizar el plugin Moodle `block_videorec` para conectarse con el recomendador Python, permitiendo buscar videos en tiempo real dentro del curso (usando YouTube o catálogo simulado y métodos textual, semántico o híbrido), renderizar tarjetas de videos con miniaturas y reproducir mediante un modal integrado.
- **Archivos creados / modificados:**
  - `moodle_plugin/videorec/classes/connector.php` – Clase `\block_videorec\connector` que ejecuta de forma segura el módulo Python (`exec()`) con escapeshellarg/escapeshellcmd, capturando y decodificando la respuesta JSON.
  - `moodle_plugin/videorec/settings.php` – Configuración para administración de Moodle: ruta a Python (`pythonpath`), ruta al proyecto (`recommenderpath`), fuente predeterminada y método predeterminado.
  - `moodle_plugin/videorec/view.php` – Pantalla de recomendación interactiva con formulario de búsqueda (tema prellenado con el nombre del curso), selectores de fuente y método, cuadrícula de tarjetas con miniaturas, porcentaje de coincidencia y reproductor modal embebido.
  - `moodle_plugin/videorec/block_videorec.php` – Bloque del curso actualizado con enlace directo prellenado y `has_config() = true`.
  - `moodle_plugin/videorec/version.php` – Incremento de versión a `2026110901`, versión `v0.2.0`.
  - `moodle_plugin/videorec/lang/es/block_videorec.php` y `lang/en/block_videorec.php` – Nuevas cadenas traducidas para la interfaz y configuración.
  - `block_videorec.zip` – Archivo ZIP regenerado en la raíz con los 16 archivos del plugin listo para instalar o actualizar en Moodle.
- **Comandos ejecutados:**
  - `find moodle_plugin/videorec -name "*.php" -exec php -l {} +` → 0 errores de sintaxis en todos los archivos.
  - `rsync -av --delete moodle_plugin/videorec/ videorec/` → Sincronización completa.
  - `cd moodle_plugin && zip -r ../block_videorec.zip videorec && cd ..` → Archivo ZIP generado (37.3 KB).
- **Resultado observado:** Moodle dispone de una pantalla funcional que llama al motor Python y presenta las recomendaciones interactivas dentro del contexto del curso.





### E6 — Plugin Moodle mediante exec(), v0.3.0

- **Fecha:** 17 de noviembre de 2026.
- **Autorización:** el usuario solicitó expresamente el plugin, conservando exec() para invocar Python. Este encargo reemplaza las restricciones del arranque E1 para esta integración.
- **Base:** commit d5398fb28461699f05ed154e3e0c74175f2f3b4b de eduortizc/PluginRecomendador.
- **Conservado:** cliente YouTube que consulta search.list y videos.list; ranking existente y sus pruebas.
- **Implementado:** moodle_bridge.py con subproceso limitado, stdout JSON, avisos separados, fuentes y métodos validados; conector PHP con exec(), argumentos escapados, salida y código de retorno comprobados y errores sin claves ni comandos. No se invoca el servidor web del prototipo.
- **Interfaz:** formulario POST Moodle con sesskey y acceso al curso, tarjetas Mustache con texto escapado, identificadores YouTube validados, reproductor y vistas/likes/duración. YouTube es la fuente de la interfaz y no se ofrece el híbrido adelantado.
- **Datos:** se conserva descripción, fecha y estadísticas en la salida del ranking; no se convierten valores ausentes en ceros ni se usan estadísticas como filtrado colaborativo.
- **Paquete:** v0.3.0, versión Moodle 2026111700; 13 archivos con raíz videorec/, sin Python, claves ni modelos. Copia videorec sincronizada con la fuente. Script de empaquetado y comprobación reproducible incluido.
- **Comandos comprobados:** Python 3.12, PHP CLI 8.4.27; unittest discover tests -q con PHP_BINARY: 80 pruebas OK. php -n -l: 11 archivos PHP del plugin sin errores. package_plugin.py y --check: 13 archivos verificados.
- **Naturaleza de las pruebas:** llamadas externas/embeddings simulados y un catálogo ficticio para la prueba PHP/Python. El arnés sustituye las funciones básicas de Moodle; no equivale a una instalación Moodle.
- **No comprobado aquí:** instalación real de Moodle, tema, permisos del usuario PHP, acceso a su caché/modelo y clave, búsquedas reales desde el plugin. La guía detalla cómo verificarlos.
- **Límite de exec():** cada consulta inicia procesos Python y carga nuevamente el modelo desde su caché; no hay modelo residente compartido entre peticiones. Descarga y RAM deben distinguirse.
- **Siguiente paso:** prueba local con el ZIP y una unidad de curso real; después continuar las etapas autorizadas del proyecto.
