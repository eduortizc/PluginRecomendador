<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
defined('MOODLE_INTERNAL') || die();

if ($ADMIN->fulltree) {
    foreach (['recommenderpath', 'pythonpath', 'modelcache'] as $name) {
        $settings->add(new admin_setting_configtext(
            'block_videorec/' . $name, get_string('setting_' . $name, 'block_videorec'),
            get_string('setting_' . $name . '_desc', 'block_videorec'), '', PARAM_RAW_TRIMMED
        ));
    }
    foreach (['timeout' => 120, 'maxcandidates' => 20] as $name => $default) {
        $settings->add(new admin_setting_configtext(
            'block_videorec/' . $name, get_string('setting_' . $name, 'block_videorec'),
            get_string('setting_' . $name . '_desc', 'block_videorec'), $default, PARAM_INT
        ));
    }
}
