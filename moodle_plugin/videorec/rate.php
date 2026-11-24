<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
require_once(__DIR__ . '/../../config.php');

$courseid = required_param('id', PARAM_INT);
$course = $DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST);
require_login($course);
$context = context_course::instance($courseid);
require_capability('moodle/course:view', $context);
if ($_SERVER['REQUEST_METHOD'] !== 'POST' || isguestuser()) {
    throw new moodle_exception('error_invalid_rating', 'block_videorec');
}
require_sesskey();
$videoid = required_param('videoid', PARAM_RAW_TRIMMED);
$rating = required_param('rating', PARAM_INT);
$cached = $SESSION->block_videorec_results[$courseid] ?? null;
$allowed = is_array($cached) ? array_column($cached['resultados'] ?? [], 'id') : [];
if (!in_array($videoid, $allowed, true)) {
    throw new moodle_exception('error_invalid_rating', 'block_videorec');
}
// The browser never chooses the owner of a rating: it comes from the Moodle session.
\block_videorec\ratings::save($courseid, (int)$USER->id, $videoid, $rating);
redirect(new moodle_url('/blocks/videorec/view.php', ['id' => $courseid, 'rated' => 1]));
