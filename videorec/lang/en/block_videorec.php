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
$string['block_description'] = 'Find YouTube videos related to the topics in this course.';
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
$string['privacy:metadata'] = 'The block stores explicit ratings per user, video and course.';

// Search interface strings
$string['search_panel_title'] = 'Search recommended videos';
$string['topic_input_label'] = 'Topic or learning unit:';
$string['topic_input_placeholder'] = 'Example: relational databases, OOP in Python...';
$string['btn_search'] = 'Recommend';
$string['source_label'] = 'Candidate source:';
$string['source_simulado'] = 'Simulated Catalog (Demo)';
$string['source_youtube'] = 'YouTube Data API v3 (Live)';
$string['method_label'] = 'Ranking method:';
$string['method_textual'] = 'Keyword matching';
$string['method_semantico'] = 'Semantic comparison';
$string['method_hibrido'] = 'Hybrid Textual + Semantic (E3)';
$string['results_title'] = 'Recommended videos';
$string['no_results_found'] = 'No recommendations with sufficient score were found for this query.';
$string['match_score'] = 'Textual score';
$string['semantic_similarity'] = 'Semantic similarity';
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
$string['setting_pythonpath_desc'] = 'Absolute path to the virtual environment Python. Leave empty to use .venv/bin/python inside the project.';
$string['setting_recommenderpath'] = 'Recomendador_Ext workspace path';
$string['setting_recommenderpath_desc'] = 'Absolute path to the Python project containing moodle_bridge.py and the recomendador package. PHP must be able to read it.';
$string['setting_default_source'] = 'Default candidate source';
$string['setting_default_source_desc'] = 'Default candidate source to use when opening the recommendation screen.';
$string['setting_default_method'] = 'Default recommendation method';
$string['setting_default_method_desc'] = 'The block automatically uses semantic analysis and collaborative combination.';


$string['setting_modelcache'] = 'Model cache (HF_HOME)';
$string['setting_modelcache_desc'] = 'Optional absolute existing directory writable by the PHP account. Use the same cache as the terminal to reuse downloaded weights.';
$string['setting_timeout'] = 'Engine time limit (seconds)';
$string['setting_timeout_desc'] = '5 to 600 seconds, default 120. Download the model in the terminal before using Moodle.';
$string['setting_maxcandidates'] = 'Video candidates per search';
$string['setting_maxcandidates_desc'] = '1 to 50, default 20. Returns up to five recommendations.';
$string['analysis_scope'] = 'Analyzes YouTube titles and descriptions and combines them with ratings from participants in this course.';
$string['score_explanation'] = 'Score from 0 to 1. Uses semantic similarity alone when ratings are insufficient. This is not a percentage of educational quality.';
$string['not_available'] = 'Not available';
$string['stats_views'] = 'Views';
$string['stats_likes'] = 'Likes';
$string['stats_duration'] = 'Duration';
$string['error_invalid_input'] = 'Enter a topic between 1 and 500 characters.';
$string['error_exec_disabled'] = 'The server does not allow exec(). Contact the administrator.';
$string['error_project_path'] = 'The administrator must configure a valid Python project path containing moodle_bridge.py.';
$string['error_python_path'] = 'No executable Python found. Check the .venv/bin/python interpreter path in the block settings.';
$string['error_cache_path'] = 'The model cache directory must exist and be writable by the server.';
$string['error_dependencies'] = 'Dependencies are missing from the configured Python. Install sentence-transformers in that virtual environment.';
$string['error_api_key'] = 'The YouTube key could not be read. Check the project .env and its permissions.';
$string['error_quota'] = 'The YouTube quota for this key is exhausted. Try again after it resets.';
$string['error_timeout'] = 'Analysis exceeded its time limit. Prepare the model in the terminal and check engine and PHP server time limits.';
$string['error_model'] = 'Analysis could not be completed. Check the model, cache and dependencies using the configured Python.';

$string['hybrid_score'] = 'Recommendation score';
$string['strategy_hybrid'] = 'Semantic content and ratings from similar users.';
$string['strategy_semantic'] = 'Semantic content: there are not enough ratings yet.';
$string['rate_video'] = 'Your rating:';
$string['choose_rating'] = 'Choose from 1 to 5';
$string['save_rating'] = 'Save rating';
$string['rating_saved'] = 'Rating saved. Press Recommend to recalculate the results.';
$string['error_invalid_rating'] = 'Invalid rating. Search for the video again and retry.';
$string['privacy:metadata:rating'] = 'Video ratings used for recommendations in each course.';
$string['privacy:metadata:rating:courseid'] = 'Course associated with the rating.';
$string['privacy:metadata:rating:userid'] = 'Moodle user who rated the video.';
$string['privacy:metadata:rating:videoid'] = 'YouTube video identifier.';
$string['privacy:metadata:rating:rating'] = 'Latest explicit rating from 1 to 5.';
$string['privacy:metadata:rating:timecreated'] = 'Time the rating was created.';
$string['privacy:metadata:rating:timemodified'] = 'Time the rating was last modified.';
$string['privacy:metadata:youtube'] = 'The topic is sent to YouTube to retrieve candidates. Ratings and users are not sent to YouTube.';
$string['privacy:metadata:youtube:searchquery'] = 'Topic entered to search for videos.';
