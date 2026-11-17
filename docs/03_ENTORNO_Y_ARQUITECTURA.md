# Entorno y arquitectura del recomendador independiente

## Entorno conocido

| Dato | Estado |
| --- | --- |
| Equipo | Mac, confirmado por el usuario. |
| Proyecto | Carpeta Recomendador_ext creada por el usuario. |
| Documentación | Subcarpeta docs. |
| Herramienta de desarrollo | Antigravity. |
| Conexión con Moodle en esta etapa | No se utilizará. |
| Código previo en el proyecto | Por inspeccionar dentro de la carpeta. |
| Python disponible | Por comprobar en el Mac. |

La captura anterior mostraba Moodle 5.1.3+ (Build: 20260217) y un aviso de cron. Se conservan como referencia para la integración futura; no forman parte del diagnóstico actual ni deben impedir el prototipo.

## Elección inicial

Si todavía no hay código, usar Python y su biblioteca estándar para E1. Es una decisión práctica propuesta para comenzar con tratamiento de texto y datos. No requiere paquetes externos, servidor web, PHP ni una instalación de Moodle.

Si hay código previo, revisar su lenguaje y estructura antes de introducir otra implementación. No asumir que Python está instalado por el hecho de trabajar en Mac.

## Estructura propuesta cuando se implemente E1

| Ruta | Responsabilidad |
| --- | --- |
| `AGENTS.md` | Instrucciones generales del proyecto. |
| `docs/` | Contexto, especificaciones y bitácora. |
| `README.md` | Cómo ejecutar el programa y sus comprobaciones. |
| `recomendador/__init__.py` | Paquete del recomendador. |
| `recomendador/__main__.py` | Entrada de consola. |
| `recomendador/catalogo.py` | Lectura y validación de candidatos. |
| `recomendador/ranking.py` | Función de puntuación independiente de la consola. |
| `data/videos_demo.json` | Catálogo marcado como simulado. |
| `tests/test_ranking.py` | Comprobaciones del comportamiento que puede fallar. |

Estas rutas son una especificación, no archivos ya generados. Crear únicamente los necesarios al ejecutar E1.

## Separación de responsabilidades

La función de ranking recibe una consulta y candidatos; devuelve una lista ordenada. No debe leer sesiones Moodle, recibir objetos propios de Moodle ni depender de una conexión de red.

La consola carga el catálogo y llama al motor. Más adelante, un cliente de YouTube podrá proporcionar candidatos mediante el mismo formato. La fuente de datos y el método de puntuación se podrán cambiar por separado.

Los perfiles y las valoraciones se modelarán dentro del recomendador sin exigir identificadores reales de Moodle. Durante las pruebas simuladas, usar identificadores de contexto y usuario etiquetados como ficticios.

## Contrato inicial de E1

Entrada pública de la función: tema no vacío, lista de candidatos y límite de resultados, con 5 por defecto.

Cada candidato tendrá:

| Campo | Contenido |
| --- | --- |
| `id` | Identificador interno, por ejemplo demo_001. |
| `titulo` | Texto del recurso ficticio. |
| `descripcion` | Texto descriptivo ficticio. |
| `origen` | Valor simulado en todos los registros de E1. |
| `url` | Valor null; no inventar URLs de YouTube. |

Salida: método utilizado, origen de los datos y resultados con identificador, título, puntuación y motivo del ordenamiento. Mantener números como números, y no rellenar posiciones con resultados sin coincidencias.

Campos como nivel, idioma y contexto se incorporarán cuando influyan realmente en el algoritmo. No declararlos implementados si solo son campos ignorados.

## Integración futura

El motor tendrá una interfaz de datos estable para que Moodle pueda proporcionarle contexto y mostrar los resultados. La forma concreta de conexión sigue abierta: se evaluará después si conviene un servicio privado, procesamiento por lotes o trasladar componentes al plugin.

No es necesario montar hoy una API HTTP. Elegirla dependerá del lugar donde se ejecute el modelo, los recursos disponibles y el despliegue que permita la institución.

Cuando se solicite integrar, comprobar la versión real de Moodle, su estructura pública, permisos y necesidades de privacidad. No codificar ahora rutas del Moodle del usuario.

## Fuentes técnicas de referencia

- [Reglas de Antigravity](https://antigravity.google/docs/rules)
- [Búsqueda con YouTube Data API](https://developers.google.com/youtube/v3/docs/search/list)
- [Permisos para descargar subtítulos](https://developers.google.com/youtube/v3/docs/captions/download)
- [Bloques Moodle 5.1](https://moodledev.io/docs/5.1/apis/plugintypes/blocks)
- [Estructura de directorios Moodle 5.1](https://moodledev.io/docs/5.1/guides/restructure)

Consultadas durante la preparación del proyecto el 29 de septiembre de 2026. Verificar las APIs al implementar cada integración.
