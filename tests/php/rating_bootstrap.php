<?php
// Minimal Moodle substitutes for executing the actual POST endpoint, not a Moodle installation.
define('MOODLE_INTERNAL', true);
define('PARAM_INT', 1);
define('PARAM_RAW_TRIMMED', 2);
define('MUST_EXIST', 2);
$mode = $argv[2];
class moodle_exception extends Exception {
    public function __construct($key, $component = '') { parent::__construct($key); }
}
class invalid_parameter_exception extends moodle_exception {}
class rating_redirect extends Exception {}
class moodle_url { public function __construct($url, $params = []) {} }
class context_course {
    public static function instance($id) { return (object)['instanceid' => $id]; }
}
class rating_db_fixture {
    public array $saved = [];
    public function get_record($table, $conditions, ...$rest) {
        return $table === 'course' ? (object)['id' => $conditions['id']] : false;
    }
    public function insert_record($table, $record) { $this->saved[] = clone $record; }
}
$DB = new rating_db_fixture();
$USER = (object)['id' => 7];
$SESSION = (object)['block_videorec_results' => [42 => ['resultados' => [['id' => 'AAAAAAA0001']]]]];
$request = ['id' => 42, 'videoid' => 'AAAAAAA0001', 'rating' => 4,
    'userid' => 999, 'sesskey' => 'valid'];
if ($mode === 'other-course') { $request['id'] = 84; }
if ($mode === 'unseen-video') { $request['videoid'] = 'BBBBBBB0002'; }
if ($mode === 'csrf') { $request['sesskey'] = 'wrong'; }
if ($mode === 'range') { $request['rating'] = 6; }
$_SERVER['REQUEST_METHOD'] = $mode === 'get' ? 'GET' : 'POST';
function required_param($key, $type) { global $request; return $request[$key]; }
function require_login($course) {}
function require_capability($capability, $context) {
    global $mode;
    if ($mode === 'no-access') { throw new moodle_exception('access_denied'); }
}
function require_sesskey() {
    global $request;
    if ($request['sesskey'] !== 'valid') { throw new moodle_exception('invalidsesskey'); }
}
function isguestuser() { global $mode; return $mode === 'guest'; }
function redirect($url) { throw new rating_redirect(); }
require_once(__DIR__ . '/blocks/videorec/classes/ratings.php');
