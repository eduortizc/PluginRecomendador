# Instrucciones para Recomendador_ext

## Alcance vigente — 24 de noviembre de 2026

El usuario solicitó implementar el flujo en código. E5 está incorporado al motor
y al buscador local mediante `hibrido_colaborativo`: umbral semántico, vecinos
de usuario con valoraciones explícitas y combinación, con respaldo por contenido.
El enriquecimiento de metadatos queda para una etapa futura. Consultar
docs/07_MOTOR_HIBRIDO.md y docs/05_SEGUIMIENTO.md. El plugin Moodle mantiene v0.3.0
y todavía no ofrece E5. No usar datos simulados como historial real ni confundir
el modo histórico `hibrido` textual-semántico con el nuevo método colaborativo.

## Integración previa — 17 de noviembre de 2026

El usuario autorizó integrar el motor existente como plugin Moodle mediante exec()
de PHP a Python local. La guía actual está en docs/06_PLUGIN_MOODLE.md y el estado
en docs/05_SEGUIMIENTO.md. La fuente del plugin es moodle_plugin/videorec/; genera
su copia videorec/ y block_videorec.zip con scripts/package_plugin.py. No confundir
la combinación léxica/semántica experimental con el híbrido colaborativo de E5.
Las restricciones de E1 conservadas abajo se aplican solo a aquella etapa histórica.
No acceder al Moodle real del usuario ni afirmar una instalación validada sin evidencia.

## Estado inicial (referencia histórica de E1)

El usuario desarrolla una tesis sobre recomendación de videos educativos y decidió comenzar con un proyecto independiente llamado `Recomendador_ext`. Los documentos están en `docs`. En esta etapa se trabaja fuera de Moodle; su integración queda para después.

Esta decisión reemplaza las instrucciones anteriores de diagnosticar la instalación de Moodle y crear primero un bloque. No acceder a Moodle, su código, base de datos, sesiones ni credenciales para completar la etapa actual.

La primera tarea es E1: un prototipo local con un catálogo simulado, según `docs/04_PRIMERA_ETAPA.md`. Este paquete contiene instrucciones; no acredita que exista código implementado.

## Lectura

- `docs/LEEME.md`: uso y mensaje de inicio.
- `docs/01_CONTEXTO_TESIS.md`: objetivos académicos.
- `docs/02_ALCANCE_Y_PLAN.md`: incrementos y criterios de evaluación.
- `docs/03_ENTORNO_Y_ARQUITECTURA.md`: estructura e interfaces propuestas.
- `docs/04_PRIMERA_ETAPA.md`: especificación de la tarea actual.
- `docs/05_SEGUIMIENTO.md`: estado, decisiones y bitácora.

Antes de trabajar, leer el seguimiento y la especificación de la tarea. Las instrucciones explícitas más recientes del usuario prevalecen sobre estos documentos.

## Desarrollo gradual

1. Inspeccionar el contenido de esta carpeta y conservar código o cambios existentes.
2. Trabajar únicamente en la etapa solicitada. El calendario no autoriza ejecutar todas las etapas.
3. Si solo hay documentación, usar Python para el primer prototipo. La propuesta utiliza su biblioteca estándar y no requiere un framework web.
4. Si ya hay una implementación en otro lenguaje, revisarla antes de duplicarla o reemplazarla; explicar cualquier incompatibilidad concreta.
5. Realizar las acciones reversibles necesarias sin pedir confirmaciones repetidas. Preguntar solo por un dato que no pueda obtenerse y afecte el trabajo.
6. Explicar brevemente qué hace cada parte, realizar las comprobaciones útiles y registrar lo observado.
7. Actualizar `docs/05_SEGUIMIENTO.md` al cerrar la tarea y detenerse al completarla.

## Límites originales de E1

- No buscar instalaciones de Moodle ni exigir PHP, cursos o usuarios de Moodle.
- No crear todavía `block_videorec`, adaptadores PHP, servidores HTTP ni una interfaz web.
- No conectar YouTube, instalar modelos ni pedir claves API durante E1.
- No crear carpetas vacías para funciones lejanas ni instalar dependencias innecesarias.
- Usar datos ficticios identificados como simulados y sin enlaces o identificadores que aparenten ser videos reales.
- Mantener el código propio en `Recomendador_ext`; no modificar la configuración global del Mac para resolver problemas sin relación con la tarea.

## Rigor y continuidad

El objetivo final conserva análisis semántico, filtrado colaborativo y un plugin Moodle. La coincidencia de palabras de E1 es una línea base de software, no el modelo híbrido ni una prueba de pertinencia pedagógica.

No inventar referencias, resultados, usuarios, horas de servicio, pruebas o métricas. Diferenciar lo propuesto, lo implementado y lo probado. Las interacciones simuladas no sirven como evidencia de eficacia con personas reales.

No volcar credenciales en código, mensajes, capturas o repositorios. Al incorporar datos reales, documentar su procedencia y los permisos de acceso necesarios.

Responder en español, con instrucciones cortas. Al finalizar, explicar qué cambió, cómo ejecutarlo, qué se comprobó y cuál es el siguiente incremento.

