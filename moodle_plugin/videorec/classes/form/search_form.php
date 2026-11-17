<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
namespace block_videorec\form;

defined('MOODLE_INTERNAL') || die();
global $CFG;
require_once($CFG->libdir . '/formslib.php');

/** Search submission protected by Moodle's forms API and sesskey. */
class search_form extends \moodleform {
    public function definition() {
        $form = $this->_form;
        $form->addElement('hidden', 'id');
        $form->setType('id', PARAM_INT);
        $form->addElement('text', 'tema', get_string('topic_input_label', 'block_videorec'),
            ['size' => 60, 'maxlength' => 500]);
        $form->setType('tema', PARAM_TEXT);
        $form->addRule('tema', null, 'required', null, 'client');
        $form->addElement('select', 'metodo', get_string('method_label', 'block_videorec'), [
            'semantico' => get_string('method_semantico', 'block_videorec'),
            'textual' => get_string('method_textual', 'block_videorec'),
        ]);
        $this->add_action_buttons(false, get_string('btn_search', 'block_videorec'));
    }

    public function validation($data, $files) {
        $errors = parent::validation($data, $files);
        if (trim($data['tema'] ?? '') === '' || \core_text::strlen($data['tema'] ?? '') > 500) {
            $errors['tema'] = get_string('error_invalid_input', 'block_videorec');
        }
        if (!in_array($data['metodo'] ?? '', ['textual', 'semantico'], true)) {
            $errors['metodo'] = get_string('error_invalid_input', 'block_videorec');
        }
        return $errors;
    }
}
