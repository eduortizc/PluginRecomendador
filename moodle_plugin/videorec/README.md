# Recomendador de videos para Moodle — v0.4.0

Instala block_videorec.zip desde Administración del sitio > Extensiones > Instalar extensiones.
El ZIP contiene la carpeta videorec; no subas el ZIP completo del repositorio a Moodle.

En los ajustes del bloque configura la ruta absoluta del proyecto Recomendador_Ext.
El intérprete predeterminado se obtiene de esa ruta más /.venv/bin/python. También
puedes indicar otro intérprete mediante su ruta absoluta.

El proyecto Python, sus dependencias y moodle_bridge.py deben estar en el mismo
servidor que ejecuta PHP. El usuario del servidor debe poder leerlos y ejecutar Python.
La clave de YouTube se configura en el .env del proyecto Python; no va en este ZIP.

Si la cuenta del servidor usa otra carpeta de usuario, configura una caché HF_HOME
existente y con permisos de escritura. Prepara el modelo con la misma cuenta/caché.
Cada consulta usa exec() y un nuevo proceso: carga el modelo desde disco, sin
mantener abierto el explorador web del prototipo. La descarga inicial solo se
repite cuando el modelo no está disponible en esa caché.

El botón Recomendar ejecuta análisis semántico de título y descripción, filtro
y ranking híbrido con valoraciones de usuarios similares del mismo curso.
Sin historial suficiente se usa contenido semántico. No hay selector de método.
Las valoraciones se guardan en la base de datos Moodle, con la identidad de la
sesión. Cada usuario puede actualizar su valoración de 1 a 5 por video y curso.
Python recibe temporalmente los IDs y valoraciones del curso y no los conserva.
Las vistas, likes y duración son informativos y no intervienen en el ranking.

La actualización crea la tabla block_videorec_rating y cambia la versión a
2026112400. El motor Python del servidor también debe actualizarse con esta rama.
En el intérprete configurado deben estar instaladas las dependencias de
requirements.txt (sentence-transformers) y disponible el modelo en su caché.

La instalación completa y el protocolo de prueba están en docs/06_PLUGIN_MOODLE.md
del repositorio. La compatibilidad con tu instalación y tema debe probarse allí.
