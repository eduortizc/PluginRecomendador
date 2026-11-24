<?php
// This file is part of Moodle - http://moodle.org/
//
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
namespace block_videorec;

defined('MOODLE_INTERNAL') || die();

/**
 * Executes the local Python engine. No HTTP service is required.
 *
 * @package block_videorec
 * @copyright 2026 Eduardo Ortiz
 */
class connector {
    /** Return data or a translated error; never expose commands, stderr or keys. */
    public static function get_recommendations(
        string $tema, string $fuente = 'youtube', string $metodo = 'hibrido_colaborativo',
        int $limite = 5, array $contexto = []
    ): array {
        if (trim($tema) === '') {
            return self::failure('error_empty_topic');
        }
        if (!in_array($fuente, ['youtube', 'simulado'], true) ||
                !in_array($metodo, ['textual', 'semantico', 'hibrido_colaborativo'], true)) {
            return self::failure('error_invalid_input');
        }
        if (!function_exists('exec')) {
            return self::failure('error_exec_disabled');
        }
        $project = trim((string)get_config('block_videorec', 'recommenderpath'));
        if ($project === '' || $project[0] !== '/' || !is_dir($project)) {
            return self::failure('error_project_path');
        }
        $project = realpath($project);
        $entry = $project . '/moodle_bridge.py';
        if (!is_readable($entry)) {
            return self::failure('error_project_path');
        }
        $python = trim((string)get_config('block_videorec', 'pythonpath'));
        if ($python === '') {
            $python = $project . '/.venv/bin/python';
        }
        // Keep the venv symlink: realpath() on Python would select the base interpreter.
        if ($python[0] !== '/' || !is_executable($python) || !is_file($python)) {
            return self::failure('error_python_path');
        }
        $timeout = max(5, min(600, (int)(get_config('block_videorec', 'timeout') ?: 120)));
        $candidates = max(1, min(50, (int)(get_config('block_videorec', 'maxcandidates') ?: 20)));
        $args = [$python, $entry, '--tema', trim($tema), '--fuente', $fuente,
            '--metodo', $metodo, '--limite', (string)max(1, min(5, $limite)),
            '--max-candidatos', (string)$candidates, '--timeout', (string)$timeout];
        $cache = trim((string)get_config('block_videorec', 'modelcache'));
        if ($cache !== '') {
            if ($cache[0] !== '/' || !is_dir($cache) || !is_writable($cache)) {
                return self::failure('error_cache_path');
            }
            $args[] = '--cache-dir';
            $args[] = $cache;
        }
        $stderr = tempnam(make_request_directory(), 'videorec-');
        if ($stderr === false) {
            return self::failure('error_executing_python');
        }
        $contextfile = null;
        if ($contexto) {
            $contextfile = tempnam(make_request_directory(), 'videorec-context-');
            $payload = json_encode($contexto, JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE);
            if ($contextfile === false || $payload === false ||
                    file_put_contents($contextfile, $payload) === false) {
                @unlink($stderr);
                if ($contextfile) {
                    @unlink($contextfile);
                }
                return self::failure('error_executing_python');
            }
            $args[] = '--contexto-json';
            $args[] = $contextfile;
        }
        // Every argument, including executable and paths, is quoted independently.
        $command = implode(' ', array_map('escapeshellarg', $args)) . ' 2>' . escapeshellarg($stderr);
        $output = [];
        $code = 1;
        try {
            exec($command, $output, $code);
        } catch (\Throwable $e) {
            return self::failure('error_executing_python');
        } finally {
            @unlink($stderr);
            if ($contextfile) {
                @unlink($contextfile);
            }
        }
        $decoded = json_decode(implode("\n", $output), true);
        if (!is_array($decoded)) {
            return self::failure('error_invalid_json');
        }
        if ($code !== 0 || isset($decoded['error'])) {
            $errors = [
                'dependencias' => 'error_dependencies',
                'clave_no_encontrada' => 'error_api_key',
                'error_lectura_env' => 'error_api_key',
                'cuota_excedida' => 'error_quota',
                'tiempo_agotado' => 'error_timeout',
                'entrada_invalida' => 'error_invalid_input',
                'motor' => 'error_model',
            ];
            $errorcode = is_array($decoded['error'] ?? null) ? ($decoded['error']['codigo'] ?? '') : '';
            return self::failure($errors[$errorcode] ?? 'error_executing_python');
        }
        if (!isset($decoded['resultados']) || !is_array($decoded['resultados'])) {
            return self::failure('error_invalid_json');
        }
        return ['success' => true, 'data' => $decoded];
    }

    /** Build an error response using a language string identifier. */
    private static function failure(string $key): array {
        return ['success' => false, 'data' => null, 'error' => get_string($key, 'block_videorec')];
    }
}
