# Alcance y plan por etapas

## Etapa vigente

Comenzar el motor de recomendación fuera de Moodle. La primera versión usa un catálogo simulado y una interfaz de consola para comprobar que puede recibir un tema y devolver resultados ordenados.

Trabajar fuera de Moodle no implica que todo el proyecto deba funcionar sin internet. En E1 no se necesitan servicios externos; YouTube se conectará cuando corresponda a una tarea posterior.

## Incrementos

| Etapa | Trabajo | Criterio para darla por terminada |
| --- | --- | --- |
| E1 | Catálogo local, consulta por tema y ranking textual sencillo. | Ejecución reproducible y casos básicos comprobados con datos simulados. |
| E2 | Recuperación de candidatos reales con YouTube Data API. | Metadatos reales y gestión de errores, cuotas y resultados vacíos. |
| E3 | Análisis semántico de título y descripción. Enriquecimiento pospuesto por indicación del usuario el 24/11/2026. | Modelo identificado y procedencia del texto registrada. |
| E4 | Contexto, valoraciones e interacciones dentro del prototipo independiente. | Señales de usuario diferenciadas y datos apropiados para experimentación. |
| E5 | Filtrado colaborativo y modelo híbrido. | Comparación reproducible con el ranking de contenido y manejo de falta de historial. |
| E6 | Adaptador y plugin Moodle. | Contexto y recomendaciones integrados en un entorno de pruebas, con permisos adecuados. |
| E7 | Evaluación con usuarios y documentación. | Resultados medidos, limitaciones, manual y evidencia para la tesis. |

La etapa E6 requiere una nueva tarea explícita del usuario. El acceso a Moodle no es una condición para completar E1 a E5.

## Requisitos del sistema final

- Recibir tema, nivel, disciplina, objetivo o posición en la secuencia didáctica e idioma preferido.
- Obtener candidatos de YouTube y sus metadatos disponibles.
- Registrar si el análisis utilizó título, descripción o transcripción autorizada.
- Generar hasta cinco recomendaciones con una explicación fiel a las señales utilizadas.
- Incorporar preferencias por fuentes académicas con criterios documentados.
- Diferenciar presentación de una recomendación, apertura, selección y valoración.
- Implementar un método colaborativo identificable y combinarlo con contenido.
- Atender usuarios o recursos sin historial mediante una alternativa explícita.
- Permitir el uso por docentes y estudiantes y, posteriormente, trasladar ese flujo a Moodle.
- Mantener evidencia suficiente para comparar versiones del algoritmo.

No presentar popularidad o acumulación de clics como filtrado colaborativo. No equiparar parecido temático con calidad pedagógica demostrada.

## Plan orientativo de ocho semanas

| Semana | Enfoque |
| --- | --- |
| 1 | E1 y definición del dominio de prueba. |
| 2 | E2, catálogo real y preparación de la recogida de valoraciones. |
| 3 | E3 y revisión de acceso a transcripciones autorizadas. |
| 4 | E4, perfiles e interacciones del prototipo. |
| 5 | E5 y comparación inicial entre modelos. |
| 6 | Definir el contrato de integración y comenzar E6 cuando el usuario lo solicite. |
| 7 | Completar integración de pruebas y ejecutar evaluación. |
| 8 | Corregir, documentar y preparar la entrega. |

Ajustar el calendario con horas reales, recursos y acceso a participantes. Si la integración se pospone, registrar su impacto en la entrega del plugin. Escribir la tesis y conservar evidencias durante todas las semanas.

## Datos y subtítulos

La descarga de subtítulos mediante la API oficial exige permisos para editar el video. Utilizar títulos y descripciones cuando sea lo disponible y planear una muestra propia o autorizada para probar transcripciones.

Conservar origen y permisos del texto; no afirmar que se analizó un video completo cuando solo se usaron sus metadatos. Revisar las condiciones de almacenamiento antes de conservar datos externos a largo plazo.

En E1 todos los registros serán ficticios y llevarán una marca inequívoca de simulación. Esos registros no cuentan como corpus real ni validación con docentes.

## Evaluación propuesta

Acordar con docentes una rúbrica de relevancia basada en tema, nivel, utilidad para el objetivo, claridad y confiabilidad. Separar los datos de ajuste del modelo y los de evaluación.

- NDCG@5 será la métrica principal prevista en la propuesta.
- Precision@5 requiere definir qué valoraciones cuentan como relevantes.
- Recall@K se limitará a un conjunto con relevancia de referencia conocida.
- La reducción de tiempo necesita comparar tareas equivalentes de búsqueda manual y asistida.
- Usabilidad y esfuerzo se evaluarán con participantes, distinguiendo puntuaciones SUS de comentarios cualitativos.

No reportar métricas de eficacia para E1. Las pruebas del programa solo demostrarán que cumple su comportamiento especificado.

## Decisiones abiertas

Dominio piloto, conjunto real de videos, método de embeddings, algoritmo colaborativo, participantes, canal para recopilar valoraciones y forma final de integración. No añadir de antemano un servicio web, una base vectorial o entrenamiento de modelos sin una necesidad comprobada.

