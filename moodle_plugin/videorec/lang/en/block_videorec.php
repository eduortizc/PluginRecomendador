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
 * English language strings for block_videorec.
 *
 * @package    block_videorec
 * @copyright  2026 Eduardo Ortiz
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'Educational Video Recommender';
$string['videorec:addinstance'] = 'Add a new Educational Video Recommender block';
$string['videorec:myaddinstance'] = 'Add a new Educational Video Recommender block to Dashboard';
$string['block_description'] = 'Educational video recommendation module linked to course learning units.';
$string['open_screen'] = 'Open recommender';
$string['only_in_course'] = 'This block is designed to be used inside a course.';
$string['pagetitle'] = 'Educational Video Recommender';
$string['status_ok_title'] = 'Plugin installed and connector active';
$string['status_ok_message'] = 'The plugin is active and connected with the external Python recommendation engine.';
$string['course_details_title'] = 'Current course details';
$string['course_name'] = 'Course name:';
$string['course_shortname'] = 'Short name:';
$string['course_id'] = 'Course ID:';
$string['current_user'] = 'Logged in user:';
$string['back_to_course'] = 'Back to course';
$string['privacy:metadata'] = 'The Educational Video Recommender block does not store personal data.';

// Search interface strings
$string['search_panel_title'] = 'Search recommended videos';
$string['topic_input_label'] = 'Topic or learning unit:';
$string['topic_input_placeholder'] = 'Example: relational databases, OOP in Python...';
$string['btn_search'] = 'Get recommendations';
$string['source_label'] = 'Candidate source:';
$string['source_simulado'] = 'Simulated Catalog (Demo)';
$string['source_youtube'] = 'YouTube Data API v3 (Live)';
$string['method_label'] = 'Ranking method:';
$string['method_textual'] = 'Textual Keyword Match (E1)';
$string['method_semantico'] = 'Semantic Embeddings (E3)';
$string['method_hibrido'] = 'Hybrid Textual + Semantic (E3)';
$string['results_title'] = 'Recommended videos';
$string['no_results_found'] = 'No recommendations with sufficient score were found for this query.';
$string['match_score'] = 'match';
$string['semantic_similarity'] = 'semantic similarity';
$string['matches_terms'] = 'Matching terms:';
$string['btn_play'] = 'Play here';
$string['btn_open_youtube'] = 'Open in YouTube ↗';
$string['simulated_notice'] = 'Simulated record without web video';
$string['close_modal'] = 'Close player';

// Errors
$string['error_empty_topic'] = 'The topic query cannot be empty.';
$string['error_executing_python'] = 'An error occurred while executing the Python recommender';
$string['error_invalid_json'] = 'The output returned by the recommender engine is not valid JSON.';

// Settings
$string['setting_pythonpath'] = 'Python binary path';
$string['setting_pythonpath_desc'] = 'Command or absolute path to the Python 3 binary (e.g., python3 or /usr/bin/python3).';
$string['setting_recommenderpath'] = 'Recomendador_Ext workspace path';
$string['setting_recommenderpath_desc'] = 'Absolute path on the server where the recommendation package resides.';
$string['setting_default_source'] = 'Default candidate source';
$string['setting_default_source_desc'] = 'Default candidate source to use when opening the recommendation screen.';
$string['setting_default_method'] = 'Default recommendation method';
$string['setting_default_method_desc'] = 'Default ranking method (textual, semantic embeddings, or hybrid).';
