<?php
// Standalone integration harness, not a Moodle installation or a live YouTube test.
define('MOODLE_INTERNAL', true);
$project = $argv[1];
$python = $argv[2];
$fixture = $argv[3];
$config = ['recommenderpath' => $project, 'pythonpath' => $python, 'timeout' => 10];
function get_config($plugin, $key) { global $config; return $config[$key] ?? false; }
function get_string($key, $plugin) { return $key; }
function make_request_directory() { return sys_get_temp_dir(); }
function check($value, $message) { if (!$value) { throw new RuntimeException($message); } }
require($project . '/moodle_plugin/videorec/classes/connector.php');
require($project . '/moodle_plugin/videorec/classes/results.php');

// Real PHP exec -> real Python bridge -> real local fixture catalog. No HTTP server.
$result = \block_videorec\connector::get_recommendations('bases de datos', 'simulado', 'textual', 2);
check($result['success'], 'exec failed: ' . json_encode($result));
check(count($result['data']['resultados']) === 2, 'limit was not preserved');
check(!isset($result['raw']) && !isset($result['cmd']), 'internal details leaked');

// Quotes, spaces and shell operators must remain part of the topic argument.
$marker = $fixture . '/must-not-exist';
$topic = "SQL'; touch " . $marker . "; #";
$result = \block_videorec\connector::get_recommendations($topic, 'simulado', 'textual');
check($result['success'] && $result['data']['consulta'] === $topic, 'topic quoting failed');
check(!file_exists($marker), 'shell injection executed');
check(!\block_videorec\connector::get_recommendations('SQL', 'youtube', 'hibrido')['success'], 'hybrid accepted');

// Use a worker fixture to verify stderr isolation and exit status handling.
$config['recommenderpath'] = $fixture;
file_put_contents($fixture . '/moodle_bridge.py', "import sys,json\nprint('{warning}',file=sys.stderr)\nprint(json.dumps({'resultados':[]}))\n");
check(\block_videorec\connector::get_recommendations('SQL')['success'], 'stderr contaminated JSON');
file_put_contents($fixture . '/moodle_bridge.py', "import json,sys\nprint(json.dumps({'error':{'codigo':'dependencias','mensaje':'SECRETO'}}))\nsys.exit(4)\n");
$result = \block_videorec\connector::get_recommendations('SQL');
check(!$result['success'] && $result['error'] === 'error_dependencies', 'dependency error lost');
check(strpos(json_encode($result), 'SECRETO') === false, 'worker details leaked');
file_put_contents($fixture . '/moodle_bridge.py', "print('this is not JSON')\n");
check(\block_videorec\connector::get_recommendations('SQL')['error'] === 'error_invalid_json', 'invalid JSON accepted');
file_put_contents($fixture . '/moodle_bridge.py', "print('{\"resultados\":[]}')\nraise SystemExit(1)\n");
check(!\block_videorec\connector::get_recommendations('SQL')['success'], 'non-zero exit accepted');

// Invalid paths and disabled exec produce a controlled configuration error.
$config['pythonpath'] = '/missing/python';
check(\block_videorec\connector::get_recommendations('SQL')['error'] === 'error_python_path', 'missing interpreter');
$config['pythonpath'] = $python;
$config['recommenderpath'] = '/missing/project';
check(\block_videorec\connector::get_recommendations('SQL')['error'] === 'error_project_path', 'missing project');

// Results use canonical YouTube URLs, preserve zero statistics and omit fake IDs.
$data = ['resultados' => [
    ['id' => 'aB_cD-eF123', 'titulo' => '<script>alert(1)</script>', 'url' => 'javascript:alert(1)',
     'vistas' => 0, 'likes' => null, 'duracion_segundos' => 3661, 'puntuacion' => 0.723],
    ['id' => "bad' onclick='x", 'titulo' => 'invalid'],
]];
$view = \block_videorec\results::for_template($data, 'semantico');
check(count($view['items']) === 1, 'invalid identifier rendered');
check($view['items'][0]['url'] === 'https://www.youtube.com/watch?v=aB_cD-eF123', 'untrusted URL used');
check($view['items'][0]['views'] === '0', 'zero views missing');
check($view['items'][0]['likes'] === 'not_available', 'missing likes changed to zero');
check($view['items'][0]['duration'] === '1:01:01', 'duration incorrect');
check($view['items'][0]['score'] === '0.723', 'score displayed as percentage');
echo "PHP exec integration OK\n";
