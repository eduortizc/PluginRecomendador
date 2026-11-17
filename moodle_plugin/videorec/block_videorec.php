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
 * Main block class for block_videorec.
 *
 * @package    block_videorec
 * @copyright  2026 Eduardo Ortiz
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Block videorec class.
 */
class block_videorec extends block_base {

    /**
     * Initializes the block.
     *
     * @return void
     */
    public function init() {
        $this->title = get_string('pluginname', 'block_videorec');
    }

    /**
     * Specifies which page types this block can appear on.
     *
     * @return array
     */
    public function applicable_formats() {
        return [
            'course-view' => true,
            'site' => false,
            'my' => false,
        ];
    }

    /**
     * Generates and returns the block content.
     *
     * @return stdClass
     */
    public function get_content() {
        global $COURSE;

        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new stdClass();
        $this->content->footer = '';

        // If not inside a specific course context.
        if (empty($COURSE->id) || $COURSE->id == SITEID) {
            $this->content->text = html_writer::tag(
                'p',
                get_string('only_in_course', 'block_videorec'),
                ['class' => 'text-muted small mb-0']
            );
            return $this->content;
        }

        $viewurl = new moodle_url('/blocks/videorec/view.php', [
            'id' => $COURSE->id,
            'tema' => $COURSE->fullname,
            'buscar' => 1,
        ]);

        $description = html_writer::tag(
            'p',
            get_string('block_description', 'block_videorec'),
            ['class' => 'small text-muted mb-2']
        );

        $button = html_writer::link(
            $viewurl,
            '🎬 ' . get_string('open_screen', 'block_videorec'),
            ['class' => 'btn btn-primary btn-sm w-100 shadow-sm']
        );

        $this->content->text = $description . html_writer::div($button, 'd-grid mt-2');

        return $this->content;
    }

    /**
     * Disallows multiple instances of this block in the same course.
     *
     * @return bool
     */
    public function instance_allow_multiple() {
        return false;
    }

    /**
     * Indicates whether the block has global configuration settings.
     *
     * @return bool
     */
    public function has_config() {
        return true;
    }
}
