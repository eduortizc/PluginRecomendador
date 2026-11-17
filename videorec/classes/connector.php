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
 * Connector class to communicate with the Python recommender engine.
 *
 * @package    block_videorec
 * @copyright  2026 Eduardo Ortiz
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace block_videorec;

defined('MOODLE_INTERNAL') || die();

/**
 * Connector service for block_videorec.
 */
class connector {

    /**
     * Executes the Python recommender and retrieves recommendations as an array.
     *
     * @param string $tema Search query / course topic.
     * @param string $fuente Source: 'simulado' or 'youtube'.
     * @param string $metodo Method: 'textual', 'semantico', or 'hibrido'.
     * @param int $limite Max results (1 to 5).
     * @return array Array with status, data, and possible error details.
     */
    public static function get_recommendations(
        string $tema,
        string $fuente = 'simulado',
        string $metodo = 'textual',
        int $limite = 5
    ): array {
        $tema = trim($tema);
        if ($tema === '') {
            return [
                'success' => false,
                'error' => get_string('error_empty_topic', 'block_videorec'),
                'data' => null,
            ];
        }

        $fuente = ($fuente === 'youtube') ? 'youtube' : 'simulado';
        if (!in_array($metodo, ['textual', 'semantico', 'hibrido'], true)) {
            $metodo = 'textual';
        }
        $limite = max(1, min(5, $limite));

        // Retrieve settings or sensible defaults.
        $pythonpath = get_config('block_videorec', 'pythonpath');
        if (empty($pythonpath)) {
            $pythonpath = 'python3';
        }

        $recommenderpath = get_config('block_videorec', 'recommenderpath');
        if (empty($recommenderpath)) {
            $recommenderpath = '/Users/eduardoortiz/Develops/Recomendador_Ext';
        }

        // Build command safely using escapeshellarg and escapeshellcmd.
        $escapeddir = escapeshellarg($recommenderpath);
        $escapedpython = escapeshellcmd($pythonpath);
        $escapedtema = escapeshellarg($tema);
        $escapedfuente = escapeshellarg($fuente);
        $escapedmetodo = escapeshellarg($metodo);

        $cmd = "cd {$escapeddir} && {$escapedpython} -m recomendador " .
               "--tema {$escapedtema} " .
               "--fuente {$escapedfuente} " .
               "--metodo {$escapedmetodo} " .
               "--limite {$limite} 2>&1";

        $output = [];
        $returncode = 0;
        exec($cmd, $output, $returncode);

        $rawtext = implode("\n", $output);

        // Find JSON block in the output (in case stderr or warning logs appeared before).
        $jsonstart = strpos($rawtext, '{');
        $jsonend = strrpos($rawtext, '}');

        if ($jsonstart === false || $jsonend === false || $jsonend < $jsonstart) {
            return [
                'success' => false,
                'error' => get_string('error_executing_python', 'block_videorec') . ': ' . $rawtext,
                'raw' => $rawtext,
                'cmd' => $cmd,
                'code' => $returncode,
            ];
        }

        $jsoncontent = substr($rawtext, $jsonstart, ($jsonend - $jsonstart + 1));
        $decoded = json_decode($jsoncontent, true);

        if ($decoded === null) {
            return [
                'success' => false,
                'error' => get_string('error_invalid_json', 'block_videorec'),
                'raw' => $rawtext,
                'cmd' => $cmd,
                'code' => $returncode,
            ];
        }

        return [
            'success' => true,
            'data' => $decoded,
            'raw' => $rawtext,
            'cmd' => $cmd,
            'code' => $returncode,
        ];
    }
}
