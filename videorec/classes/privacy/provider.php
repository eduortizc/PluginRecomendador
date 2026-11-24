<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
namespace block_videorec\privacy;
defined('MOODLE_INTERNAL') || die();

use core_privacy\local\metadata\collection;
use core_privacy\local\request\approved_contextlist;
use core_privacy\local\request\approved_userlist;
use core_privacy\local\request\contextlist;
use core_privacy\local\request\userlist;
use core_privacy\local\request\writer;

/** Export and remove course-scoped explicit ratings using Moodle's Privacy API. */
class provider implements \core_privacy\local\metadata\provider,
        \core_privacy\local\request\plugin\provider,
        \core_privacy\local\request\core_userlist_provider {
    public static function get_metadata(collection $collection): collection {
        $fields = [];
        foreach (['courseid', 'userid', 'videoid', 'rating', 'timecreated', 'timemodified'] as $field) {
            $fields[$field] = 'privacy:metadata:rating:' . $field;
        }
        $collection->add_database_table('block_videorec_rating', $fields, 'privacy:metadata:rating');
        $collection->add_external_location_link('youtube',
            ['searchquery' => 'privacy:metadata:youtube:searchquery'], 'privacy:metadata:youtube');
        return $collection;
    }

    public static function get_contexts_for_userid(int $userid): contextlist {
        $list = new contextlist();
        $list->add_from_sql('SELECT DISTINCT c.id FROM {context} c
            JOIN {block_videorec_rating} r ON r.courseid = c.instanceid
            WHERE c.contextlevel = :level AND r.userid = :userid',
            ['level' => CONTEXT_COURSE, 'userid' => $userid]);
        return $list;
    }

    public static function get_users_in_context(userlist $userlist) {
        $context = $userlist->get_context();
        if ($context instanceof \context_course) {
            $userlist->add_from_sql('userid',
                'SELECT DISTINCT userid FROM {block_videorec_rating} WHERE courseid = :courseid',
                ['courseid' => $context->instanceid]);
        }
    }

    public static function export_user_data(approved_contextlist $contextlist) {
        global $DB;
        foreach ($contextlist->get_contexts() as $context) {
            if (!$context instanceof \context_course) {
                continue;
            }
            $records = $DB->get_records('block_videorec_rating',
                ['courseid' => $context->instanceid, 'userid' => $contextlist->get_user()->id]);
            $ratings = [];
            foreach ($records as $record) {
                $ratings[] = (object)['videoid' => $record->videoid, 'rating' => $record->rating,
                    'timecreated' => $record->timecreated, 'timemodified' => $record->timemodified];
            }
            if ($ratings) {
                writer::with_context($context)->export_data(
                    [get_string('pluginname', 'block_videorec')], (object)['ratings' => $ratings]);
            }
        }
    }

    public static function delete_data_for_all_users_in_context(\context $context) {
        global $DB;
        if ($context instanceof \context_course) {
            $DB->delete_records('block_videorec_rating', ['courseid' => $context->instanceid]);
        }
    }

    public static function delete_data_for_user(approved_contextlist $contextlist) {
        global $DB;
        foreach ($contextlist->get_contexts() as $context) {
            if ($context instanceof \context_course) {
                $DB->delete_records('block_videorec_rating',
                    ['courseid' => $context->instanceid, 'userid' => $contextlist->get_user()->id]);
            }
        }
    }

    public static function delete_data_for_users(approved_userlist $userlist) {
        global $DB;
        $context = $userlist->get_context();
        if (!$context instanceof \context_course || !$userlist->get_userids()) {
            return;
        }
        [$insql, $params] = $DB->get_in_or_equal($userlist->get_userids(), SQL_PARAMS_NAMED);
        $params['courseid'] = $context->instanceid;
        $DB->delete_records_select('block_videorec_rating', "courseid = :courseid AND userid $insql", $params);
    }
}
