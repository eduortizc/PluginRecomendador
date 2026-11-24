# Plugin Moodle con motor híbrido por exec() — v0.4.0

## Qué cambia

El bloque ofrece un tema y un botón **Recomendar**. Cada consulta obtiene candidatos
reales de YouTube, calcula la similitud semántica de título y descripción, aplica
el umbral y combina el contenido con valoraciones de usuarios similares del curso.
Se usa `hibrido_colaborativo` automáticamente, sin seleccionar etapas manualmente.
Cuando falta evidencia colaborativa, cada video mantiene su puntuación semántica.
El enriquecimiento de metadatos queda pendiente.

El usuario procede de la sesión Moodle. Las valoraciones explícitas de 1 a 5 se
guardan en `block_videorec_rating`, con una fila por usuario, curso y video; una nueva
valoración actualiza la anterior. La matriz solo incluye participantes con matrícula
activa, sin suspensión ni baja. No mezcla cursos ni utiliza historiales simulados.
La búsqueda no registra impresiones o aperturas como valoraciones.

El conector PHP ejecuta `moodle_bridge.py` mediante `exec()`. El contexto del curso
se entrega en un archivo JSON temporal privado y se elimina tanto al completar la
consulta como al producirse errores. El motor no escribe historiales de Moodle en
el proyecto Python. Los nombres, correos y valoraciones no se envían a YouTube.

## Descargar cambios y generar el ZIP en Antigravity

Dentro del proyecto, estando en la rama `codex/motor-hibrido`:

```bash
git pull --ff-only origin codex/motor-hibrido
python3 scripts/package_plugin.py
python3 scripts/package_plugin.py --check
```

Se crea **block_videorec.zip** en la raíz. Ese archivo es el plugin instalable.
No hace falta ejecutar `python3 -m recomendador --web`. No subir a Moodle el ZIP
del repositorio completo.

## Preparar el Python que ejecuta Moodle

El ZIP contiene PHP, plantillas y la definición de su tabla. El proyecto Python,
sus dependencias y el modelo se preparan en el mismo servidor o contenedor donde
se ejecuta PHP. Una ruta del Mac no sirve dentro de Docker si no está montada.
También hay que actualizar allí `moodle_bridge.py` y `recomendador/` con esta rama.

Si el entorno virtual ya existe, se reutiliza. Si no existe:

```bash
python3 -m venv .venv
```

Para instalar dependencias en el intérprete correcto:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c "import sentence_transformers; print('Dependencia disponible')"
```

El mensaje de dependencia ausente de la captura indica que el Python utilizado no
encuentra sentence-transformers. Instalarlo con otro Python no resuelve ese caso.
Moodle debe apuntar al Python de este entorno virtual, no al Python global.

Con la clave de YouTube en el `.env` local, preparar/verificar el motor sin abrir
el prototipo web:

```bash
.venv/bin/python moodle_bridge.py --tema "bases de datos" --timeout 600
```

Esta consulta usa el híbrido con respaldo semántico, pues no recibe contexto Moodle.
Permite preparar la descarga del modelo. Si se configura `HF_HOME`, utilizar la
misma carpeta con `--cache-dir /RUTA/ABSOLUTA/CACHE` y en los ajustes del bloque.
La cuenta que ejecuta PHP debe poder leer el proyecto, la clave y el modelo.
Cada consulta crea un proceso Python nuevo; no hay modelo residente entre peticiones.

## Actualizar en Moodle

1. Subir `block_videorec.zip` desde Administración del sitio > Extensiones > Instalar extensiones.
2. Completar la actualización a **v0.4.0**, versión **2026112400**. Se crea la tabla
   de valoraciones tanto en instalaciones nuevas como al actualizar v0.3.0.
3. Revisar los ajustes del bloque: ruta del proyecto, intérprete Python, caché,
   número de candidatos y tiempo máximo. El método es automático.
4. Abrir un curso, añadir el bloque si aún no está y pulsar Abrir recomendador.
5. Escribir un tema y pulsar Recomendar. Valorar videos con el selector de 1 a 5
   y Guardar valoración. Pulsar Recomendar de nuevo para recalcular.

La pantalla reutiliza en la sesión los últimos resultados del curso al guardar una
valoración; no repite automáticamente búsquedas de YouTube. Solo permite valorar
videos de ese último conjunto. La identidad nunca se recibe desde el formulario.
La petición de valoración exige POST, sesskey, sesión no invitada y acceso al curso.

Ejemplo de rutas si el proyecto sigue en el Mac informado por el usuario:

| Ajuste | Valor |
| --- | --- |
| Proyecto | `/Users/eduardoortiz/Develops/Recomendador_Ext` |
| Python | `/Users/eduardoortiz/Develops/Recomendador_Ext/.venv/bin/python` |
| Candidatos | 20 |
| Tiempo máximo | 120 segundos; preparar la descarga inicial antes de usar Moodle |
| Caché | La misma del modelo preparado, accesible a la cuenta PHP |

Las rutas deben corresponder al servidor real. Instalar solo el ZIP sin actualizar
el Python del servidor puede dejar un puente anterior que no admite el método nuevo.

## Datos y mantenimiento

La API de privacidad de Moodle permite localizar, exportar y borrar valoraciones
por usuario y curso, y borrar los datos de un contexto. Se eliminan también al
borrar el curso. Las últimas recomendaciones solo se conservan en la sesión del
usuario. El modelo no se entrena con estas valoraciones: el componente colaborativo
calcula vecinos en cada consulta. Las vistas y likes son informativos.

La fuente es `moodle_plugin/videorec/`. `scripts/package_plugin.py` genera la copia
`videorec/` y `block_videorec.zip`. No editar únicamente la copia generada.

## Comprobaciones y límites

La suite independiente prueba el puente PHP/Python real con catálogo ficticio,
embeddings controlados y valoraciones sintéticas, incluida la combinación, el filtro,
el respaldo y la eliminación de archivos temporales. No utiliza un Moodle real.
`moodle_plugin/videorec/tests/ratings_test.php` incluye pruebas para ejecutar dentro
de un entorno PHPUnit de Moodle sobre almacenamiento, aislamiento y borrado; no
se consideran ejecutadas por la suite Python independiente.

```bash
python3 -m unittest discover tests -v
```

Con PHP fuera del PATH, indicar `PHP_BINARY=/ruta/php`. El entorno del usuario
todavía debe comprobar actualización de la tabla, permisos, interfaz y búsquedas
reales. No se accedió al Moodle del usuario ni se declara eficacia pedagógica.

## Referencias técnicas

- https://moodledev.io/docs/5.1/apis/subsystems/privacy
- https://moodledev.io/general/development/tools/xmldb
- https://moodledev.io/docs/5.1/apis/plugintypes/blocks
- https://www.php.net/manual/en/function.exec.php
