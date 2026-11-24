# Motor semántico y colaborativo — 24 de noviembre de 2026

## Ejecutar el buscador local

Desde la carpeta del proyecto, con el entorno virtual que ya contiene
sentence-transformers y la clave de YouTube configurada:

```bash
python3 -m recomendador --web
```

Abre http://127.0.0.1:8080. La fuente inicial es YouTube real y el método inicial
es Híbrido (contenido + colaborativo). Escribe un identificador local para guardar
valoraciones con las estrellas. Repite una búsqueda después de valorar para
recalcular las recomendaciones. El prototipo permite cambiar el identificador
para probar distintos historiales; no autentica usuarios ni suplanta cuentas Moodle.

No se precargan personas ni valoraciones ficticias en el flujo real. Las búsquedas
anónimas funcionan por contenido. Mostrar o abrir un video se registra como evento,
pero E5 utiliza únicamente las valoraciones explícitas de 1 a 5.

## Flujo implementado

1. Recuperar candidatos con el cliente YouTube existente.
2. Calcular embeddings de título y descripción respecto al tema.
3. Aplicar un umbral semántico, inicialmente 0.15.
4. Predecir afinidad mediante valoraciones de usuarios similares.
5. Combinar ambas puntuaciones y ordenar todos los aceptados.
6. Devolver hasta cinco resultados.

Se conserva el contexto recibido, pero nivel educativo y objetivos no se deducen
ni filtran automáticamente. El enriquecimiento de metadatos queda pendiente y
no participa en esta versión. No se analizan transcripciones.

## Algoritmo colaborativo y combinación

Implementación inicial por vecinos de usuario, sin dependencias nuevas:

- Matriz usuario-video con promedio de valoraciones explícitas de cada par.
- Similitud coseno calculada únicamente sobre videos valorados por ambos usuarios.
- Mínimo de dos videos comunes por vecino; las ausencias se ignoran.
- Hasta diez vecinos por candidato, ordenados por similitud e identificador.
- Predicción: promedio de sus valoraciones, ponderado por similitud.
- Normalización de 1-5 a 0-1 mediante `(valor - 1) / 4`.
- Puntuación final: `0.7 * semántica + 0.3 * colaborativa`.

El filtro semántico se aplica antes de la predicción. Una valoración alta no rescata
un video que no pase ese filtro. Se mantienen los videos previamente valorados:
es un buscador de recursos y no se fuerza la exclusión del historial.

Sin usuario, sin valoraciones, sin vecinos suficientes o sin valoraciones de los
vecinos para un candidato, ese candidato conserva el 100% de su puntuación semántica.
La ausencia de evidencia se representa con `null`, no con cero. Una predicción
colaborativa de cero sí es válida: corresponde al extremo inferior de la escala.

El JSON incluye puntuaciones separadas, peso efectivo, número de vecinos, motivo
de respaldo y conteos del filtro. El peso, umbral y mínimo de coincidencias son
parámetros iniciales, sin ajuste experimental ni eficacia pedagógica demostrada.
El coseno sobre valoraciones positivas puede discriminar poco con historiales
pequeños; deberá compararse con otras variantes usando datos de evaluación.

## Consola

```bash
python3 -m recomendador --tema "bases de datos" --fuente youtube --metodo hibrido_colaborativo --usuario alumno_01
python3 -m recomendador --tema "bases de datos" --fuente youtube --metodo hibrido_colaborativo --usuario alumno_01 --peso-semantico 0.8 --umbral-semantico 0.2
python3 -m recomendador --fuente youtube --ver-matriz
```

Los eventos reales del prototipo se guardan en `data/interacciones.json`.
El catálogo simulado utiliza `data/interacciones_pruebas.json`, separado del real.
Ambos empiezan vacíos y están excluidos de Git y de la entrega. Se puede especificar
otro archivo con `--interacciones RUTA` en consola. El archivo histórico
`interacciones_demo.json` se conserva como ejemplo y no se carga por defecto.

El modo antiguo `--metodo hibrido` conserva su comportamiento textual-semántico
para compatibilidad; no es el método colaborativo. `--alpha` solo afecta a ese
modo antiguo. El nuevo método se llama `hibrido_colaborativo`.

## Alcance y validación

El motor y el buscador local incorporan E5. Desde el plugin Moodle v0.4.0, el
formulario ejecuta directamente el híbrido colaborativo con la identidad de la
sesión y las valoraciones del curso. La base de datos Moodle conserva una sola
valoración por usuario, video y curso: al volver a valorar se actualiza la anterior.
Se incluyen únicamente participantes con matrícula activa, sin suspensión ni baja.
La matriz se entrega a Python mediante un archivo temporal, eliminado al terminar;
no se mezcla con los archivos de interacciones del prototipo. No se envían nombres,
correos ni valoraciones a YouTube. No se accedió al Moodle del usuario.

Las pruebas de E5 usan valoraciones ficticias y embeddings controlados. Comprueban
reordenamiento antes del límite, filtro previo, ausencia de historial, cero frente
a ausencia, persistencia y un recorrido HTTP de valoración y recomendación. No
constituyen una evaluación con personas ni una búsqueda real de YouTube.
