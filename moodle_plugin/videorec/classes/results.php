<?php
// @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
namespace block_videorec;

defined('MOODLE_INTERNAL') || die();

/** Prepare plain text and validated URLs for an escaped Mustache template. */
class results {
    public static function for_template(array $data, string $method): array {
        $items = [];
        foreach (array_slice($data['resultados'] ?? [], 0, 5) as $item) {
            if (!is_array($item)) {
                continue;
            }
            $id = (string)($item['id'] ?? '');
            // Only real YouTube identifiers can create thumbnails, players or links.
            if (!preg_match('/^[A-Za-z0-9_-]{11}$/D', $id)) {
                continue;
            }
            $description = (string)($item['descripcion'] ?? '');
            preg_match('/^.{0,280}/us', $description, $match);
            $short = $match[0] ?? '';
            $score = is_numeric($item['puntuacion'] ?? null) ? (float)$item['puntuacion'] : 0.0;
            $items[] = [
                'videoid' => $id,
                'title' => (string)($item['titulo'] ?? ''),
                'channel' => (string)($item['canal'] ?? ''),
                'description' => $short . ($short !== $description ? '…' : ''),
                'score' => number_format(max(0, min(1, $score)), 3, '.', ''),
                'strategy' => get_string(($item['estrategia'] ?? '') === 'semantico_colaborativo'
                    ? 'strategy_hybrid' : 'strategy_semantic', 'block_videorec'),
                'thumbnail' => 'https://i.ytimg.com/vi/' . $id . '/hqdefault.jpg',
                'url' => 'https://www.youtube.com/watch?v=' . $id,
                'embed' => 'https://www.youtube-nocookie.com/embed/' . $id,
                'views' => self::statistic($item['vistas'] ?? null),
                'likes' => self::statistic($item['likes'] ?? null),
                'duration' => self::duration($item['duracion_segundos'] ?? null),
            ];
        }
        return [
            'items' => $items, 'hasresults' => (bool)$items, 'count' => count($items),
            'scorelabel' => get_string($method === 'hibrido_colaborativo' ? 'hybrid_score'
                : ($method === 'semantico' ? 'semantic_similarity' : 'match_score'), 'block_videorec'),
        ];
    }

    private static function statistic($value): string {
        return is_numeric($value) && $value >= 0
            ? number_format((float)$value, 0, '.', ',') : get_string('not_available', 'block_videorec');
    }

    private static function duration($value): string {
        if (!is_numeric($value) || $value < 0) {
            return get_string('not_available', 'block_videorec');
        }
        $seconds = (int)$value;
        return $seconds >= 3600
            ? sprintf('%d:%02d:%02d', intdiv($seconds, 3600), intdiv($seconds % 3600, 60), $seconds % 60)
            : sprintf('%d:%02d', intdiv($seconds, 60), $seconds % 60);
    }
}
