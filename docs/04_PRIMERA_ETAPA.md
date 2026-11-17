# E1 Prototipo local con catálogo simulado

## Objetivo

Disponer de un programa independiente que reciba un tema, compare textos de un catálogo pequeño y devuelva hasta cinco coincidencias ordenadas.

La etapa comprueba el flujo del programa. Todavía no implementa análisis semántico, aprendizaje colaborativo ni un plugin Moodle.

## Preparación

1. Leer las instrucciones de la raíz y los documentos de docs.
2. Revisar archivos existentes dentro de Recomendador_ext.
3. Si hay código previo, identificar lo que pueda reutilizarse.
4. Si solo hay documentación, comprobar el Python disponible mediante una consulta de versión. Usar su biblioteca estándar.
5. Si falta un intérprete utilizable, informar el dato concreto y el paso mínimo para resolverlo. No buscar Moodle como alternativa.

No hace falta diagnosticar servicios web, PHP, cron ni bases de datos de Moodle.

## Programa solicitado

Separar lectura del catálogo, puntuación y entrada de consola. Usar la estructura de `03_ENTORNO_Y_ARQUITECTURA.md`.

El usuario podrá ejecutar desde la raíz, si se usa Python:

```bash
python3 -m recomendador --tema "bases de datos"
```

Esta es la interfaz que se implementará, no un comando que ya pueda ejecutarse con los Markdown actuales.

Aceptar también `--limite` como entero entre 1 y 5. El catálogo de demostración debe encontrarse mediante una ruta determinada por la ubicación del proyecto, sin asumir una ruta absoluta en el Mac.

## Catálogo

Crear al menos ocho registros ficticios sobre temas diferenciados. Incluir ejemplos relacionados con bases de datos, programación y otros temas para poder comprobar coincidencias y ausencias.

Cada registro tendrá id, titulo, descripcion, origen y url según el contrato. Todos usarán `origen: "simulado"` y `url: null`.

Etiquetar claramente el archivo como catálogo de prueba. No atribuir esos registros a canales o personas reales ni asignarles identificadores que aparenten ser de YouTube.

## Línea base textual

Para E1, usar una regla sencilla y explicable:

1. Normalizar tema, títulos y descripciones a minúsculas.
2. Quitar diferencias de acentuación y separar palabras completas.
3. Excluir una lista pequeña y explícita de palabras funcionales, documentada en el código.
4. Comparar los términos únicos del tema con los términos del título y la descripción de cada candidato.
5. Calcular la puntuación como cantidad de términos de consulta coincidentes dividida entre cantidad de términos de consulta utilizables.
6. Ordenar de mayor a menor puntuación. Resolver empates por id para mantener un resultado determinista.
7. Devolver únicamente candidatos con puntuación positiva, hasta el límite solicitado.

La coincidencia debe ser por palabras completas. Si una consulta queda vacía tras normalizarla, devolver un mensaje claro y evitar divisiones por cero.

Esta fórmula es una decisión para la demostración. No llamarla embeddings, inteligencia semántica, personalización o recomendación híbrida. No utilizarla para afirmar calidad pedagógica.

## Salida

Mostrar un resultado estructurado y legible con:

- Método: coincidencia textual.
- Datos: simulados.
- Consulta recibida.
- Resultados: id, título, puntuación y palabras coincidentes que explican el resultado.

Puede usarse JSON como salida de consola. Si no existen coincidencias, devolver una lista vacía con un mensaje comprensible. No inventar resultados para llegar a cinco.

Distinguir falta de resultados de un error al leer o validar el catálogo.

## Comprobaciones necesarias

| Caso | Resultado esperado |
| --- | --- |
| Consulta con términos presentes | Aparecen los recursos correspondientes en orden descendente. |
| Variación de mayúsculas o acentos | Produce las mismas coincidencias. |
| Consulta sin coincidencias | Lista vacía, sin errores. |
| Consulta vacía o solo palabras excluidas | Mensaje de validación, sin división por cero. |
| Puntuaciones empatadas | Orden estable por identificador. |
| Límite inválido | Error de entrada claro. |
| Catálogo ausente, JSON inválido o registros incompletos | Error diferenciable de una búsqueda vacía. |

Usar un pequeño conjunto de pruebas con la biblioteca estándar para comprobar normalización, ranking y casos vacíos. El README debe explicar la ejecución del programa y de las pruebas.

## Entregables al finalizar E1

- Código mínimo del recomendador independiente.
- Catálogo de demostración.
- Pruebas ejecutadas y resultados observados.
- README con comandos y ejemplo obtenido al ejecutar.
- Bitácora actualizada en `05_SEGUIMIENTO.md`.

No añadir llamadas externas, modelos, frontend, adaptadores Moodle ni dependencias innecesarias en esta tarea. Completar E1 y detenerse.

## Siguiente incremento

E2 sustituirá o complementará el catálogo simulado con candidatos de YouTube. La selección inicial seguirá siendo una base sobre la que incorporar después análisis semántico e interacciones.
