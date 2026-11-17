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

$method = get_config('block_videorec', 'default_method');
if (!in_array($method, ['textual', 'semantico'], true)) {
    $method = 'semantico';
}
$form = new \block_videorec\form\search_form($url);
$form->set_data(['id' => $courseid, 'tema' => $course->fullname, 'metodo' => $method]);
$submitted = $form->get_data();

echo $OUTPUT->header();
echo $OUTPUT->heading(get_string('pagetitle', 'block_videorec'), 2);
echo html_writer::div(format_string($course->fullname, true, ['context' => $context]), 'alert alert-info');
echo html_writer::div(get_string('analysis_scope', 'block_videorec'), 'alert alert-secondary');
$form->display();

if ($submitted) {
    require_sesskey();
    // Release this user's session lock during a potentially expensive analysis.
    \core\session\manager::write_close();
    $response = \block_videorec\connector::get_recommendations(
        $submitted->tema, 'youtube', $submitted->metodo, 5
    );
    if (!$response['success']) {
        echo $OUTPUT->notification($response['error'], 'notifyproblem');
    } else {
        $view = \block_videorec\results::for_template($response['data'], $submitted->metodo);
        echo $OUTPUT->render_from_template('block_videorec/results', $view);
    }
}
echo html_writer::link(new moodle_url('/course/view.php', ['id' => $courseid]),
    get_string('back_to_course', 'block_videorec'), ['class' => 'btn btn-secondary mb-3']);
echo $OUTPUT->footer();
