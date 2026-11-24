<?php
// Executes the real endpoint with the minimal test bootstrap installed as config.php.
$root = $argv[1];
$mode = $argv[2];
$redirected = false;
$rejected = false;
try {
    require($root . '/blocks/videorec/rate.php');
} catch (rating_redirect $e) {
    $redirected = true;
} catch (moodle_exception $e) {
    $rejected = true;
}
if ($mode === 'valid') {
    if (!$redirected || count($DB->saved) !== 1 || $DB->saved[0]->userid !== 7 ||
            $DB->saved[0]->courseid !== 42 || $DB->saved[0]->rating !== 4) {
        throw new RuntimeException('Authenticated rating owner or persistence failed');
    }
} else if (!$rejected || $DB->saved) {
    throw new RuntimeException('Unauthorized rating was accepted: ' . $mode);
}
echo "Rating endpoint OK: $mode\n";
