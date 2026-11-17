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
$string['block_description'] = 'Módulo para la recomendación de videos educativos vinculados a las unidades del curso.';
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
$string['privacy:metadata'] = 'El bloque de Recomendador de Videos Educativos no almacena datos personales.';

// Search interface strings
$string['search_panel_title'] = 'Búsqueda de videos recomendados';
$string['topic_input_label'] = 'Tema o unidad de aprendizaje:';
$string['topic_input_placeholder'] = 'Ejemplo: bases de datos relacionales, POO en Python...';
$string['btn_search'] = 'Obtener recomendaciones';
$string['source_label'] = 'Fuente de candidatos:';
$string['source_simulado'] = 'Catálogo Simulado (Demo)';
$string['source_youtube'] = 'YouTube Data API v3 (Real)';
$string['method_label'] = 'Método de ranking:';
$string['method_textual'] = 'Coincidencia Textual (E1)';
$string['method_semantico'] = 'Semántico con Embeddings (E3)';
$string['method_hibrido'] = 'Híbrido Textual + Semántico (E3)';
$string['results_title'] = 'Recomendaciones obtenidas';
$string['no_results_found'] = 'No se encontraron recomendaciones con puntuación suficiente para esta búsqueda.';
$string['match_score'] = 'coincidencia';
$string['semantic_similarity'] = 'similitud semántica';
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
$string['setting_pythonpath_desc'] = 'Comando o ruta absoluta al binario de Python 3 (ej: python3 o /usr/bin/python3).';
$string['setting_recommenderpath'] = 'Ruta del proyecto Recomendador_Ext';
$string['setting_recommenderpath_desc'] = 'Ruta absoluta en el servidor donde reside el paquete recomendador.';
$string['setting_default_source'] = 'Fuente de candidatos predeterminada';
$string['setting_default_source_desc'] = 'Fuente utilizada por defecto al abrir la pantalla de recomendación.';
$string['setting_default_method'] = 'Método de recomendación predeterminado';
$string['setting_default_method_desc'] = 'Método de cálculo predeterminado (textual, semántico con embeddings o híbrido).';
