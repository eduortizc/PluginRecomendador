<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
namespace block_videorec;
defined('MOODLE_INTERNAL') || die();

/** Remove ratings when their course is removed. */
class observers {
    public static function course_deleted(\core\event\course_deleted $event): void {
        global $DB;
        $DB->delete_records('block_videorec_rating', ['courseid' => $event->objectid]);
    }
}
