<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
namespace block_videorec;
defined('MOODLE_INTERNAL') || die();

/** Tests requiring an initialized Moodle PHPUnit environment.
 * @covers \block_videorec\ratings
 * @covers \block_videorec\privacy\provider
 */
final class ratings_test extends \advanced_testcase {
    public function test_latest_rating_and_course_isolation(): void {
        global $DB;
        $this->resetAfterTest();
        $course = $this->getDataGenerator()->create_course();
        $other = $this->getDataGenerator()->create_course();
        $user = $this->getDataGenerator()->create_user();
        $outsider = $this->getDataGenerator()->create_user();
        $this->getDataGenerator()->enrol_user($user->id, $course->id);
        ratings::save($course->id, $user->id, 'AAAAAAA0001', 2);
        ratings::save($course->id, $user->id, 'AAAAAAA0001', 5);
        ratings::save($other->id, $user->id, 'BBBBBBB0002', 1);
        ratings::save($course->id, $outsider->id, 'AAAAAAA0001', 1);
        $this->assertSame(['u_' . $user->id => ['AAAAAAA0001' => 5]], ratings::matrix($course->id));
        $this->assertSame(1, $DB->count_records('block_videorec_rating',
            ['courseid' => $course->id, 'userid' => $user->id]));
        $this->assertSame(['AAAAAAA0001' => 5], ratings::for_user($course->id, $user->id));
        $DB->set_field('user', 'suspended', 1, ['id' => $user->id]);
        $this->assertSame([], ratings::matrix($course->id));
    }

    public function test_privacy_deletes_only_approved_user_and_course(): void {
        global $DB;
        $this->resetAfterTest();
        $course = $this->getDataGenerator()->create_course();
        $other = $this->getDataGenerator()->create_course();
        $user = $this->getDataGenerator()->create_user();
        $neighbour = $this->getDataGenerator()->create_user();
        ratings::save($course->id, $user->id, 'AAAAAAA0001', 5);
        ratings::save($other->id, $user->id, 'AAAAAAA0001', 4);
        ratings::save($course->id, $neighbour->id, 'AAAAAAA0001', 3);
        $context = \context_course::instance($course->id);
        $approved = new \core_privacy\local\request\approved_contextlist($user, 'block_videorec', [$context->id]);
        \block_videorec\privacy\provider::delete_data_for_user($approved);
        $this->assertFalse($DB->record_exists('block_videorec_rating',
            ['courseid' => $course->id, 'userid' => $user->id]));
        $this->assertTrue($DB->record_exists('block_videorec_rating',
            ['courseid' => $other->id, 'userid' => $user->id]));
        $this->assertTrue($DB->record_exists('block_videorec_rating',
            ['courseid' => $course->id, 'userid' => $neighbour->id]));
    }

    public function test_invalid_rating_is_rejected(): void {
        $this->expectException(\invalid_parameter_exception::class);
        ratings::save(1, 1, 'AAAAAAA0001', 6);
    }
}
