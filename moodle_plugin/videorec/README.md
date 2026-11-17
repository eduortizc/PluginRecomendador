# Recomendador de videos para Moodle — v0.3.0

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

La búsqueda usa YouTube real y permite ranking textual o semántico de título y
descripción. Las vistas, likes y duración se muestran si la API los devuelve;
no se usan como filtrado colaborativo ni como garantía de calidad educativa.
No se registran perfiles, usuarios Moodle ni interacciones en esta versión.

La instalación completa y el protocolo de prueba están en docs/06_PLUGIN_MOODLE.md
del repositorio. La compatibilidad con tu instalación y tema debe probarse allí.
