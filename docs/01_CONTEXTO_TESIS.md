# Contexto de la tesis y etapa independiente

## Documentos de origen

Este contexto procede de `Propuesta de tesis versión finalv2(4).docx`, correspondiente a Seminario de Tesis I, y `Tesis_V1.0.docx`, borrador de los capítulos 1 y 2 para Seminario de Tesis II.

La propuesta identifica a Eduardo Alberto Ortiz Caamal como autor, a la Facultad de Matemáticas de la Universidad Autónoma de Yucatán como institución y al Dr. Victor Hugo Menéndez Domínguez como asesor. Estos datos académicos no permiten inferir permisos o cuentas del entorno de desarrollo.

El usuario dispone de aproximadamente dos meses, desarrolla el proyecto como parte de su servicio social y quiere avanzar por etapas. Trabaja en Mac y usará Antigravity.

## Decisión vigente del usuario

El 29 de septiembre de 2026 aclaró que empezará fuera de Moodle, en la carpeta `Recomendador_ext`, con documentación dentro de `docs`.

Esta decisión cambia la secuencia de implementación. El primer resultado será un programa independiente. El objetivo académico final sigue siendo un plugin para Moodle; desarrollar el motor aparte no completa por sí solo ese objetivo.

## Problema y objetivo general

El trabajo busca reducir el esfuerzo necesario para encontrar videos de YouTube apropiados para un contexto académico. El plugin previsto recomendará recursos según el contenido disponible, el perfil contextual y las interacciones de los usuarios.

La pregunta de investigación plantea si es posible automatizar esas recomendaciones mediante algoritmos híbridos cuando los metadatos de origen carecen de suficiente descripción pedagógica.

La hipótesis propone una mejora en pertinencia y una reducción del tiempo y esfuerzo de búsqueda. Son resultados que deberán evaluarse.

## Objetivos que deben conservarse

- Fundamentar el proyecto con el estado del arte de recomendación educativa.
- Diseñar un modelo que combine análisis de contenido y filtrado colaborativo.
- Aplicar procesamiento de lenguaje natural para enriquecer metadatos.
- Considerar nivel, disciplina, secuencia didáctica y preferencia por fuentes académicas.
- Implementar el sistema dentro de Moodle en una etapa posterior.
- Evaluar ranking, usabilidad y experiencia de los participantes.

## Componentes previstos

| Componente | Propósito |
| --- | --- |
| Contenido | Comparar el texto y las características de los recursos con el contexto académico. |
| Colaborativo | Identificar patrones entre usuarios y recursos mediante interacciones relevantes. |
| Híbrido | Combinar ambas señales con una estrategia explícita y evaluable. |
| PLN | Analizar texto y generar representaciones o descriptores. |
| Contexto | Expresar las necesidades del curso y las preferencias pertinentes. |

La primera coincidencia de palabras de E1 solo comprobará el flujo de entrada, ordenamiento y salida. Después deberá incorporarse el análisis semántico y la combinación con interacciones.

## Metodología y documentación

La propuesta utiliza Design Science Research: identificar el problema, diseñar, construir, demostrar, evaluar y documentar. Cada incremento debe dejar una decisión justificada, código verificable y evidencia real de las comprobaciones.

En el borrador siguen pendientes antecedentes, planteamiento del problema, justificación y alcance. Su marco teórico necesita citas verificadas y la bibliografía todavía requiere revisión. No tratar todas las referencias heredadas como comprobadas.

El cronograma de la propuesta contiene fechas inconsistentes y cubre un periodo mayor. El calendario de este paquete es orientativo para el desarrollo del piloto.

## Pendientes académicos

Definir el curso o dominio piloto, participantes, rúbrica de pertinencia, horas semanales, texto autorizado de los videos y protocolo de evaluación. Si las restricciones de datos exigen cambiar un objetivo aprobado, documentar el efecto para revisarlo con el asesor.
