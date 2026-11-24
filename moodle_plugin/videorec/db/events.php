<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
defined('MOODLE_INTERNAL') || die();
$observers = [
    ['eventname' => '\core\event\course_deleted', 'callback' => '\block_videorec\observers::course_deleted'],
];
