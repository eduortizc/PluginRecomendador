# Plugin Moodle con exec() — v0.3.0

## Qué entrega esta versión

Un bloque de curso llamado **Recomendador de Videos Educativos** abre un formulario.
Al enviarlo, PHP ejecuta el Python del entorno virtual con `exec()` y llama a
`moodle_bridge.py`. Este puente utiliza las funciones existentes de YouTube y ranking,
devuelve JSON y termina. No requiere tener abierto `python -m recomendador --web`.

La búsqueda del plugin siempre consulta YouTube real. Se ofrecen los métodos textual
y semántico; no se presenta el híbrido de la tesis como implementado. Las tarjetas
incluyen título, descripción, canal, puntuación de 0 a 1, vistas, likes y duración
cuando esos datos estén disponibles. Una cifra no disponible se muestra como tal,
sin inventar ceros. Las estadísticas no modifican el ranking ni son filtrado colaborativo.

Solo se analiza título y descripción. Esta versión no entrena el modelo, infiere
objetivos educativos, lee materiales Moodle ni procesa transcripciones. No registra
usuarios ni interacciones Moodle en el JSON de demostración de E4.

## Preparar Python en el Mac

Desde la carpeta del proyecto actualizado:

```bash
cd /Users/eduardoortiz/Develops/Recomendador_Ext
```

Si el entorno ya está instalado, se reutiliza. Para prepararlo en otro equipo:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install sentence-transformers
```

Conserva la clave real en el archivo `.env` local, que no se incluye en Git ni en el
ZIP del plugin. La clave debe poder leerse desde la cuenta que ejecuta PHP.

Prueba el mismo puente que llamará Moodle, con una consulta real:

```bash
.venv/bin/python moodle_bridge.py --tema "bases de datos relacionales" --metodo semantico --timeout 120
```

La salida estándar debe ser un objeto JSON con `datos: "youtube"` y `resultados`.
Si devuelve `error`, resuélvelo antes de probar Moodle. El puente limita la ejecución
del trabajador mediante un subproceso con tiempo máximo; los avisos no se mezclan
con el JSON. Un error termina con código de salida distinto de cero.

El modelo debe prepararse antes de la primera búsqueda en Moodle para evitar que
una descarga grande supere el tiempo de PHP o del servidor web. Si usas una caché
HF_HOME explícita, utiliza exactamente la misma carpeta en la terminal y en Moodle:

```bash
.venv/bin/python moodle_bridge.py --tema "bases de datos" --metodo semantico --cache-dir /RUTA/ABSOLUTA/CACHE --timeout 600
```

La carpeta de caché debe existir y tener permisos adecuados. El archivo de pesos
del modelo predeterminado ocupa aproximadamente 471 MB; dependencias y RAM se
contabilizan por separado. No se descarga nuevamente por cada consulta si la misma
caché conserva el modelo. Sin embargo, cada llamada exec() crea procesos nuevos y
vuelve a cargar los pesos en memoria: no conserva el modelo entre peticiones.

## Instalar o actualizar en Moodle

1. Descarga **block_videorec.zip** de esta versión, no el ZIP completo del repositorio.
2. Entra como administrador y abre **Administración del sitio > Extensiones > Instalar extensiones**.
3. Sube el ZIP. Su carpeta raíz es `videorec` y su componente es `block_videorec`.
4. Completa la instalación o actualización a **v0.3.0**, versión `2026111700`.
5. Busca los ajustes del bloque en **Extensiones > Bloques > Recomendador de Videos Educativos**.

Si copias los archivos manualmente, Moodle 5.1 utiliza `public/blocks/videorec/`;
Moodle 4.5 y 5.0 utilizan `blocks/videorec/`. Usa la estructura real de tu instalación.
Después abre Administración del sitio para que Moodle aplique la actualización.

Configura estos valores para el Mac descrito por el usuario:

| Ajuste | Valor |
| --- | --- |
| Ruta del proyecto | `/Users/eduardoortiz/Develops/Recomendador_Ext` |
| Intérprete Python | `/Users/eduardoortiz/Develops/Recomendador_Ext/.venv/bin/python` |
| Método predeterminado | Semántico |
| Videos candidatos | 20 |
| Tiempo máximo del motor | 120 segundos |
| Caché del modelo | Vacía si PHP usa la misma cuenta/caché; de lo contrario indicar la carpeta existente correspondiente. |

El entorno Python debe estar en el mismo equipo o contenedor donde se ejecuta PHP.
Un Moodle dentro de Docker no ve automáticamente las rutas del Mac: requiere montar
el proyecto e instalar Python en ese entorno, y configurar las rutas internas.
El tiempo máximo del trabajador no sustituye el de PHP-FPM, Apache, Nginx o el proxy;
sus límites deben permitir que termine una consulta. No se cambian globalmente desde el plugin.

## Usar el bloque

1. Entra a un curso con permisos de edición y activa el modo de edición.
2. Añade **Recomendador de Videos Educativos** a los bloques del curso.
3. Pulsa **Abrir recomendador**. Abrir la pantalla no consulta YouTube automáticamente.
4. Escribe el tema o unidad, selecciona Semántico o Textual y envía el formulario.
5. Revisa las tarjetas; puedes abrir YouTube o desplegar el reproductor embebido.

La página comprueba sesión y acceso al curso. El formulario POST utiliza la API de
formularios de Moodle y su sesskey. Los títulos se escapan mediante Mustache, y las
URLs se construyen desde identificadores YouTube válidos. La clave no se envía al
navegador ni se pasa como argumento del comando. No se muestran comandos ni stderr
a los estudiantes. La reproducción y las miniaturas contactan con YouTube.

## Archivos y empaquetado

- Fuente del plugin: `moodle_plugin/videorec/`.
- Copia sincronizada: `videorec/`, conservada por compatibilidad con el proyecto anterior.
- ZIP instalable: `block_videorec.zip`.
- Puente ejecutado por PHP: `moodle_bridge.py`, junto al motor Python, fuera del ZIP.

Edita la fuente y genera el paquete mediante:

```bash
python3 scripts/package_plugin.py
python3 scripts/package_plugin.py --check
```

## Validación y límites

Durante esta entrega se ejecutaron **80 pruebas** con Python 3.12 y PHP CLI 8.4:
incluyen PHP exec() real a Python, argumentos con comillas y espacios, JSON, errores,
estadísticas cero/no disponibles y conservación de los datos de YouTube en el ranking.
Se comprobó la sintaxis de los 11 archivos PHP del plugin. Los datos externos de las
pruebas son simulados; no acreditan eficacia educativa ni una llamada real de YouTube
durante esta revisión.

Para repetir las pruebas con PHP disponible:

```bash
python3 -m unittest discover tests -v
```

Si PHP no está en PATH, configura `PHP_BINARY` con su ruta. En su ausencia se omite
la prueba de integración PHP, y la suite lo indica. El archivo
`tests/php/connector_smoke.php` es un arnés con funciones Moodle mínimas sustituidas:
comprueba el proceso PHP/Python pero no equivale a ejecutar Moodle.

**Pendiente en el entorno del usuario:** instalar el ZIP, verificar el tema de Moodle,
los permisos de la cuenta PHP, el modelo y la clave, y ejecutar búsquedas reales desde
el curso. No se accedió al Moodle del usuario ni se declara comprobada esa instalación.

## Referencias técnicas

- https://moodledev.io/docs/5.1/apis/plugintypes/blocks
- https://moodledev.io/docs/5.1/apis/subsystems/form
- https://moodledev.io/docs/5.1/guides/templates
- https://moodledev.io/docs/5.1/guides/restructure
- https://www.php.net/manual/en/function.exec.php
