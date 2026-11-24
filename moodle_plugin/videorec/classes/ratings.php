<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
namespace block_videorec;
defined('MOODLE_INTERNAL') || die();

/** Explicit ratings stored by Moodle, scoped to one course. */
class ratings {
    public static function save(int $courseid, int $userid, string $videoid, int $rating): void {
        global $DB;
        if ($courseid < 1 || $userid < 1 || !preg_match('/^[A-Za-z0-9_-]{11}$/D', $videoid) ||
                $rating < 1 || $rating > 5) {
            throw new \invalid_parameter_exception('Invalid video rating');
        }
        $conditions = ['courseid' => $courseid, 'userid' => $userid, 'videoid' => $videoid];
        $record = $DB->get_record('block_videorec_rating', $conditions);
        if ($record) {
            $record->rating = $rating;
            $record->timemodified = time();
            $DB->update_record('block_videorec_rating', $record);
        } else {
            $record = (object)($conditions + ['rating' => $rating,
                'timecreated' => time(), 'timemodified' => time()]);
            $DB->insert_record('block_videorec_rating', $record);
        }
    }

    /** Only active course participants are included as collaborative neighbours. */
    public static function matrix(int $courseid): array {
        global $DB;
        [$enrolledsql, $params] = get_enrolled_sql(\context_course::instance($courseid), '', 0, true);
        $params['ratingcourse'] = $courseid;
        $records = $DB->get_records_sql("SELECT r.* FROM {block_videorec_rating} r
            JOIN {user} u ON u.id = r.userid AND u.deleted = 0 AND u.suspended = 0
            JOIN ($enrolledsql) enrolled ON enrolled.id = r.userid
            WHERE r.courseid = :ratingcourse ORDER BY r.id", $params);
        $matrix = [];
        foreach ($records as $record) {
            $matrix['u_' . $record->userid][$record->videoid] = (int)$record->rating;
        }
        return $matrix;
    }

    public static function for_user(int $courseid, int $userid): array {
        global $DB;
        $records = $DB->get_records('block_videorec_rating', ['courseid' => $courseid, 'userid' => $userid]);
        $ratings = [];
        foreach ($records as $record) {
            $ratings[$record->videoid] = (int)$record->rating;
        }
        return $ratings;
    }
}
