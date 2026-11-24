<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
defined('MOODLE_INTERNAL') || die();

/** Create the ratings table when updating an existing installation. */
function xmldb_block_videorec_upgrade($oldversion) {
    global $DB;
    if ($oldversion < 2026112400) {
        $manager = $DB->get_manager();
        $table = new xmldb_table('block_videorec_rating');
        if (!$manager->table_exists($table)) {
            $manager->install_from_xmldb_file(__DIR__ . '/install.xml');
        }
        upgrade_block_savepoint(true, 2026112400, 'videorec');
    }
    return true;
}
