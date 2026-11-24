<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Spanish language strings for block_videorec.
 *
 * @package    block_videorec
 * @copyright  2026 Eduardo Ortiz
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'Recomendador de Videos Educativos';
$string['videorec:addinstance'] = 'Añadir un nuevo bloque de Recomendador de Videos Educativos';
$string['videorec:myaddinstance'] = 'Añadir un nuevo bloque de Recomendador de Videos Educativos al Área personal';
$string['block_description'] = 'Busca videos de YouTube relacionados con los temas de este curso.';
$string['open_screen'] = 'Abrir recomendador';
$string['only_in_course'] = 'Este bloque está diseñado para utilizarse dentro de un curso.';
$string['pagetitle'] = 'Recomendador de Videos Educativos';
$string['status_ok_title'] = 'Plugin instalado y conector activo';
$string['status_ok_message'] = 'El plugin se encuentra activo y conectado con el motor de recomendación en Python.';
$string['course_details_title'] = 'Información del curso actual';
$string['course_name'] = 'Nombre del curso:';
$string['course_shortname'] = 'Nombre corto:';
$string['course_id'] = 'Identificador del curso (ID):';
$string['current_user'] = 'Usuario con sesión activa:';
$string['back_to_course'] = 'Volver al curso';
$string['privacy:metadata'] = 'El bloque almacena valoraciones explícitas por usuario, video y curso.';

// Search interface strings
$string['search_panel_title'] = 'Búsqueda de videos recomendados';
$string['topic_input_label'] = 'Tema o unidad de aprendizaje:';
$string['topic_input_placeholder'] = 'Ejemplo: bases de datos relacionales, POO en Python...';
$string['btn_search'] = 'Recomendar';
$string['source_label'] = 'Fuente de candidatos:';
$string['source_simulado'] = 'Catálogo Simulado (Demo)';
$string['source_youtube'] = 'YouTube Data API v3 (Real)';
$string['method_label'] = 'Método de ranking:';
$string['method_textual'] = 'Coincidencia de palabras';
$string['method_semantico'] = 'Comparación semántica';
$string['method_hibrido'] = 'Híbrido Textual + Semántico (E3)';
$string['results_title'] = 'Recomendaciones obtenidas';
$string['no_results_found'] = 'No se encontraron recomendaciones con puntuación suficiente para esta búsqueda.';
$string['match_score'] = 'Puntuación textual';
$string['semantic_similarity'] = 'Similitud semántica';
$string['matches_terms'] = 'Términos coincidentes:';
$string['btn_play'] = 'Reproducir aquí';
$string['btn_open_youtube'] = 'Abrir en YouTube ↗';
$string['simulated_notice'] = 'Video simulado sin enlace web';
$string['close_modal'] = 'Cerrar reproductor';

// Errors
$string['error_empty_topic'] = 'El tema de consulta no puede estar vacío.';
$string['error_executing_python'] = 'Ocurrió un error al ejecutar el motor de recomendación en Python';
$string['error_invalid_json'] = 'La salida devuelta por el motor de recomendación no contiene un JSON válido.';

// Settings
$string['setting_pythonpath'] = 'Ruta del intérprete Python';
$string['setting_pythonpath_desc'] = 'Ruta absoluta al Python del entorno virtual. Si se deja vacía, se usa .venv/bin/python dentro del proyecto.';
$string['setting_recommenderpath'] = 'Ruta del proyecto Recomendador_Ext';
$string['setting_recommenderpath_desc'] = 'Ruta absoluta del proyecto Python que contiene moodle_bridge.py y la carpeta recomendador. Debe ser accesible para PHP.';
$string['setting_default_source'] = 'Fuente de candidatos predeterminada';
$string['setting_default_source_desc'] = 'Fuente utilizada por defecto al abrir la pantalla de recomendación.';
$string['setting_default_method'] = 'Método de recomendación predeterminado';
$string['setting_default_method_desc'] = 'El flujo del bloque utiliza análisis semántico y combinación colaborativa automáticamente.';


$string['setting_modelcache'] = 'Caché del modelo (HF_HOME)';
$string['setting_modelcache_desc'] = 'Opcional: carpeta absoluta, existente y escribible por la cuenta que ejecuta PHP. Para reutilizar el modelo descargado, utiliza la misma caché que en la terminal.';
$string['setting_timeout'] = 'Tiempo máximo del motor (segundos)';
$string['setting_timeout_desc'] = 'Entre 5 y 600 segundos. Por defecto 120. Prepara la descarga inicial del modelo en la terminal antes de usar Moodle.';
$string['setting_maxcandidates'] = 'Videos candidatos por búsqueda';
$string['setting_maxcandidates_desc'] = 'Entre 1 y 50, por defecto 20. Se devuelven hasta cinco recomendaciones.';
$string['analysis_scope'] = 'Se analizan los títulos y descripciones de YouTube y se combinan con valoraciones de participantes de este curso.';
$string['score_explanation'] = 'Puntuación de 0 a 1. Si faltan valoraciones suficientes, se utiliza solo la similitud semántica. No representa un porcentaje de calidad pedagógica.';
$string['not_available'] = 'No disponible';
$string['stats_views'] = 'Visualizaciones';
$string['stats_likes'] = 'Me gusta';
$string['stats_duration'] = 'Duración';
$string['error_invalid_input'] = 'Escribe un tema de entre 1 y 500 caracteres.';
$string['error_exec_disabled'] = 'El servidor no permite ejecutar exec(). Contacta al administrador.';
$string['error_project_path'] = 'El administrador debe configurar una ruta válida del proyecto Python que contenga moodle_bridge.py.';
$string['error_python_path'] = 'No se encuentra un Python ejecutable. Revisa la ruta del intérprete .venv/bin/python en los ajustes del bloque.';
$string['error_cache_path'] = 'La carpeta de caché del modelo debe existir y ser escribible por el servidor.';
$string['error_dependencies'] = 'Faltan dependencias en el Python configurado. El administrador debe instalar sentence-transformers en ese entorno virtual.';
$string['error_api_key'] = 'No se pudo leer la clave de YouTube. El administrador debe revisar el .env del proyecto y sus permisos.';
$string['error_quota'] = 'Se agotó la cuota de YouTube para esta clave. Inténtalo cuando se restablezca.';
$string['error_timeout'] = 'El análisis superó el tiempo configurado. Prepara el modelo en la terminal y revisa el límite del motor y del servidor PHP.';
$string['error_model'] = 'No se pudo completar el análisis. El administrador debe comprobar el modelo, la caché y las dependencias con el Python configurado.';

$string['hybrid_score'] = 'Puntuación de recomendación';
$string['strategy_hybrid'] = 'Contenido semántico y valoraciones de usuarios similares.';
$string['strategy_semantic'] = 'Contenido semántico: todavía faltan valoraciones suficientes.';
$string['rate_video'] = 'Tu valoración:';
$string['choose_rating'] = 'Selecciona de 1 a 5';
$string['save_rating'] = 'Guardar valoración';
$string['rating_saved'] = 'Valoración guardada. Pulsa Recomendar para recalcular los resultados.';
$string['error_invalid_rating'] = 'La valoración no es válida. Vuelve a buscar el video e inténtalo de nuevo.';
$string['privacy:metadata:rating'] = 'Valoraciones de videos para las recomendaciones de cada curso.';
$string['privacy:metadata:rating:courseid'] = 'Curso al que pertenece la valoración.';
$string['privacy:metadata:rating:userid'] = 'Usuario de Moodle que valora el video.';
$string['privacy:metadata:rating:videoid'] = 'Identificador del video de YouTube.';
$string['privacy:metadata:rating:rating'] = 'Última valoración explícita de 1 a 5.';
$string['privacy:metadata:rating:timecreated'] = 'Fecha de creación de la valoración.';
$string['privacy:metadata:rating:timemodified'] = 'Fecha de la última modificación.';
$string['privacy:metadata:youtube'] = 'El tema se envía a YouTube para recuperar candidatos. Las valoraciones y los usuarios no se envían a YouTube.';
$string['privacy:metadata:youtube:searchquery'] = 'Tema escrito para buscar videos.';
