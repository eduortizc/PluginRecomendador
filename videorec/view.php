<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
require_once(__DIR__ . '/../../config.php');

$courseid = required_param('id', PARAM_INT);
$course = $DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST);
require_login($course);
$context = context_course::instance($course->id);
require_capability('moodle/course:view', $context);

$url = new moodle_url('/blocks/videorec/view.php', ['id' => $courseid]);
$PAGE->set_url($url);
$PAGE->set_context($context);
$PAGE->set_course($course);
$PAGE->set_pagelayout('incourse');
$PAGE->set_cacheable(false);
$PAGE->set_title(get_string('pagetitle', 'block_videorec'));
$PAGE->set_heading($course->fullname);
$PAGE->navbar->add(get_string('pluginname', 'block_videorec'), $url);

$method = 'hibrido_colaborativo';
$cached = $SESSION->block_videorec_results[$courseid] ?? null;
$form = new \block_videorec\form\search_form($url);
$form->set_data(['id' => $courseid, 'tema' => $cached['consulta'] ?? $course->fullname]);
$submitted = $form->get_data();

echo $OUTPUT->header();
echo $OUTPUT->heading(get_string('pagetitle', 'block_videorec'), 2);
echo html_writer::div(format_string($course->fullname, true, ['context' => $context]), 'alert alert-info');
echo html_writer::div(get_string('analysis_scope', 'block_videorec'), 'alert alert-secondary');
$form->display();

if (optional_param('rated', 0, PARAM_INT)) {
    echo $OUTPUT->notification(get_string('rating_saved', 'block_videorec'), 'notifysuccess');
}
$data = null;
if ($submitted) {
    require_sesskey();
    $enginecontext = ['usuario_id' => 'u_' . $USER->id, 'curso_id' => (int)$courseid,
        'matriz_utilidad' => (object)\block_videorec\ratings::matrix($courseid)];
    $response = \block_videorec\connector::get_recommendations(
        $submitted->tema, 'youtube', $method, 5, $enginecontext
    );
    if (!$response['success']) {
        echo $OUTPUT->notification($response['error'], 'notifyproblem');
    } else {
        $data = $response['data'];
        // Retain only the latest result set per course in this user's session.
        $SESSION->block_videorec_results[$courseid] = $data;
    }
} else if (is_array($cached)) {
    $data = $cached;
}
if ($data !== null) {
    $view = \block_videorec\results::for_template($data, $method);
    $view['ratingurl'] = (new moodle_url('/blocks/videorec/rate.php'))->out(false);
    $view['courseid'] = $courseid;
    $view['sesskey'] = sesskey();
    $view['canrate'] = !isguestuser();
    $userratings = \block_videorec\ratings::for_user($courseid, (int)$USER->id);
    foreach ($view['items'] as &$item) {
        $item['ratingoptions'] = [];
        for ($value = 1; $value <= 5; $value++) {
            $item['ratingoptions'][] = ['value' => $value,
                'selected' => ($userratings[$item['videoid']] ?? 0) === $value];
        }
    }
    unset($item);
    echo $OUTPUT->render_from_template('block_videorec/results', $view);
}
echo html_writer::link(new moodle_url('/course/view.php', ['id' => $courseid]),
    get_string('back_to_course', 'block_videorec'), ['class' => 'btn btn-secondary mb-3']);
echo $OUTPUT->footer();
