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
 * Settings for block_videorec.
 *
 * @package    block_videorec
 * @copyright  2026 Eduardo Ortiz
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if ($ADMIN->fulltree) {
    // Setting: Path to Python binary.
    $settings->add(new admin_setting_configtext(
        'block_videorec/pythonpath',
        get_string('setting_pythonpath', 'block_videorec'),
        get_string('setting_pythonpath_desc', 'block_videorec'),
        'python3',
        PARAM_RAW_TRIMMED
    ));

    // Setting: Path to Recomendador_Ext workspace.
    $settings->add(new admin_setting_configtext(
        'block_videorec/recommenderpath',
        get_string('setting_recommenderpath', 'block_videorec'),
        get_string('setting_recommenderpath_desc', 'block_videorec'),
        '/Users/eduardoortiz/Develops/Recomendador_Ext',
        PARAM_RAW_TRIMMED
    ));

    // Setting: Default source.
    $settings->add(new admin_setting_configselect(
        'block_videorec/default_source',
        get_string('setting_default_source', 'block_videorec'),
        get_string('setting_default_source_desc', 'block_videorec'),
        'simulado',
        [
            'simulado' => get_string('source_simulado', 'block_videorec'),
            'youtube' => get_string('source_youtube', 'block_videorec'),
        ]
    ));

    // Setting: Default recommendation method.
    $settings->add(new admin_setting_configselect(
        'block_videorec/default_method',
        get_string('setting_default_method', 'block_videorec'),
        get_string('setting_default_method_desc', 'block_videorec'),
        'textual',
        [
            'textual' => get_string('method_textual', 'block_videorec'),
            'semantico' => get_string('method_semantico', 'block_videorec'),
            'hibrido' => get_string('method_hibrido', 'block_videorec'),
        ]
    ));
}

