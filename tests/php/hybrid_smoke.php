<?php
// Standalone PHP/Python integration with fictitious ratings and controlled embeddings.
define('MOODLE_INTERNAL', true);
$project = $argv[1];
$python = $argv[2];
$fixture = $argv[3];
$requestdir = $fixture . '/request';
mkdir($requestdir);
$config = ['recommenderpath' => $project, 'pythonpath' => $python, 'timeout' => 10];
function get_config($plugin, $key) { global $config; return $config[$key] ?? false; }
function get_string($key, $plugin) { return $key; }
function make_request_directory() { global $requestdir; return $requestdir; }
function check($value, $message) { if (!$value) { throw new RuntimeException($message); } }
require($project . '/moodle_plugin/videorec/classes/connector.php');
require($project . '/moodle_plugin/videorec/classes/results.php');
$context = ['usuario_id' => 'u_1', 'curso_id' => 42, 'matriz_utilidad' => [
    'u_1' => ['COMMON00001' => 5, 'COMMON00002' => 1],
    'u_2' => ['COMMON00001' => 5, 'COMMON00002' => 1,
        'AAAAAAA0001' => 1, 'BBBBBBB0002' => 5, 'CCCCCCC0003' => 5],
]];
$result = \block_videorec\connector::get_recommendations('SQL', 'simulado', 'hibrido_colaborativo', 5, $context);
check($result['success'], 'hybrid failed: ' . json_encode($result));
$data = $result['data'];
check($data['metodo'] === 'hibrido_colaborativo', 'wrong method');
check($data['contexto']['curso_id'] === 42, 'course lost');
check($data['resultados'][0]['id'] === 'BBBBBBB0002', 'collaborative ranking lost');
check(abs($data['resultados'][0]['puntuacion'] - 0.79) < 0.000001, 'wrong combined score');
check(count($data['resultados']) === 3, 'semantic gate not applied before collaboration');
check($data['resultados'][2]['estrategia'] === 'respaldo_semantico', 'new video has no fallback');
$view = \block_videorec\results::for_template($data, 'hibrido_colaborativo');
check($view['items'][0]['videoid'] === 'BBBBBBB0002', 'rating id not preserved');
check($view['items'][0]['strategy'] === 'strategy_hybrid', 'hybrid explanation lost');
check($view['scorelabel'] === 'hybrid_score', 'wrong score label');
check(glob($requestdir . '/*') === [], 'temporary data not deleted');
$context['matriz_utilidad'] = (object)[];
$result = \block_videorec\connector::get_recommendations('SQL', 'simulado', 'hibrido_colaborativo', 5, $context);
check($result['success'], 'empty Moodle matrix rejected');
check($result['data']['resultados'][0]['id'] === 'AAAAAAA0001', 'semantic fallback order lost');
check($result['data']['resultados'][0]['puntuacion'] === 0.8, 'missing history penalizes content');
$context['matriz_utilidad'] = ['u_1' => ['AAAAAAA0001' => 9]];
$result = \block_videorec\connector::get_recommendations('SQL', 'simulado', 'hibrido_colaborativo', 5, $context);
check(!$result['success'], 'invalid rating accepted');
check(glob($requestdir . '/*') === [], 'temporary data leaked on failure');
echo "PHP hybrid integration OK\n";
