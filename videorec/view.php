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
 * Interactive recommendation view page for block_videorec.
 *
 * @package    block_videorec
 * @copyright  2026 Eduardo Ortiz
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(__DIR__ . '/../../config.php');

// Parameter: course ID.
$courseid = required_param('id', PARAM_INT);
$tema     = optional_param('tema', '', PARAM_TEXT);
$fuente   = optional_param('fuente', '', PARAM_ALPHA);
$metodo   = optional_param('metodo', '', PARAM_ALPHA);
$hassearched = optional_param('buscar', 0, PARAM_INT);

// Retrieve course.
$course = $DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST);

// Verify user login and course access permissions.
require_login($course);

$context = context_course::instance($course->id);
require_capability('moodle/course:view', $context);

// Defaults from config if not submitted.
if (empty($fuente)) {
    $fuente = get_config('block_videorec', 'default_source') ?: 'simulado';
}
if (empty($metodo)) {
    $metodo = get_config('block_videorec', 'default_method') ?: 'textual';
}

// Default topic suggestion is course fullname if empty.
$displaytema = ($tema !== '') ? $tema : $course->fullname;

// Page setup.
$pageurl = new moodle_url('/blocks/videorec/view.php', [
    'id' => $course->id,
    'tema' => $tema,
    'fuente' => $fuente,
    'metodo' => $metodo,
]);
$PAGE->set_url($pageurl);
$PAGE->set_context($context);
$PAGE->set_course($course);
$PAGE->set_pagelayout('incourse');
$PAGE->set_title(get_string('pagetitle', 'block_videorec'));
$PAGE->set_heading($course->fullname);

// Breadcrumb navigation.
$PAGE->navbar->add(get_string('pluginname', 'block_videorec'), $pageurl);

echo $OUTPUT->header();

echo $OUTPUT->heading(get_string('pagetitle', 'block_videorec'), 2);

// Course context banner.
$coursebadge = html_writer::tag('span', s($course->fullname), ['class' => 'fw-bold text-primary']);
$userbadge = html_writer::tag('span', fullname($USER), ['class' => 'text-muted']);
$infobar = html_writer::div(
    "📚 " . get_string('course_name', 'block_videorec') . " {$coursebadge} (ID: {$course->id}) | 👤 {$userbadge}",
    'alert alert-info py-2 px-3 mb-4 shadow-sm'
);
echo $infobar;

// Search & Configuration Form.
$formaction = new moodle_url('/blocks/videorec/view.php', ['id' => $course->id]);
$formhtml = '<form method="get" action="' . $formaction->out_omit_querystring() . '" class="card shadow-sm p-4 mb-4">';
$formhtml .= '<input type="hidden" name="id" value="' . s($course->id) . '">';
$formhtml .= '<input type="hidden" name="buscar" value="1">';

$formhtml .= '<h5 class="card-title mb-3">🔍 ' . get_string('search_panel_title', 'block_videorec') . '</h5>';

// Topic input.
$formhtml .= '<div class="mb-3">';
$formhtml .= '<label for="id_tema" class="form-label fw-bold">' . get_string('topic_input_label', 'block_videorec') . '</label>';
$formhtml .= '<div class="input-group">';
$formhtml .= '<input type="text" id="id_tema" name="tema" class="form-control form-control-lg" ' .
             'placeholder="' . s(get_string('topic_input_placeholder', 'block_videorec')) . '" ' .
             'value="' . s($displaytema) . '" required>';
$formhtml .= '<button type="submit" class="btn btn-primary btn-lg px-4">🚀 ' . get_string('btn_search', 'block_videorec') . '</button>';
$formhtml .= '</div>';
$formhtml .= '</div>';

// Options row: Source & Method.
$formhtml .= '<div class="row g-3 align-items-center">';

// Source selector.
$formhtml .= '<div class="col-md-6">';
$formhtml .= '<label for="id_fuente" class="form-label small text-muted mb-1">' . get_string('source_label', 'block_videorec') . '</label>';
$formhtml .= '<select id="id_fuente" name="fuente" class="form-select">';
$formhtml .= '<option value="youtube"' . ($fuente === 'youtube' ? ' selected' : '') . '>📺 ' . get_string('source_youtube', 'block_videorec') . '</option>';
$formhtml .= '<option value="simulado"' . ($fuente === 'simulado' ? ' selected' : '') . '>📚 ' . get_string('source_simulado', 'block_videorec') . '</option>';
$formhtml .= '</select>';
$formhtml .= '</div>';

// Method selector.
$formhtml .= '<div class="col-md-6">';
$formhtml .= '<label for="id_metodo" class="form-label small text-muted mb-1">' . get_string('method_label', 'block_videorec') . '</label>';
$formhtml .= '<select id="id_metodo" name="metodo" class="form-select">';
$formhtml .= '<option value="textual"' . ($metodo === 'textual' ? ' selected' : '') . '>🔤 ' . get_string('method_textual', 'block_videorec') . '</option>';
$formhtml .= '<option value="semantico"' . ($metodo === 'semantico' ? ' selected' : '') . '>✨ ' . get_string('method_semantico', 'block_videorec') . '</option>';
$formhtml .= '<option value="hibrido"' . ($metodo === 'hibrido' ? ' selected' : '') . '>⚖️ ' . get_string('method_hibrido', 'block_videorec') . '</option>';
$formhtml .= '</select>';
$formhtml .= '</div>';

$formhtml .= '</div>'; // End row
$formhtml .= '</form>';

echo $formhtml;

// Execute recommendation if a search query is present.
if ($hassearched || $tema !== '') {
    $searchquery = ($tema !== '') ? $tema : $displaytema;
    $response = \block_videorec\connector::get_recommendations($searchquery, $fuente, $metodo, 5);

    if (!$response['success']) {
        $errormsg = html_writer::tag('h5', '⚠️ ' . get_string('error', 'moodle'), ['class' => 'alert-heading']);
        $errorbody = html_writer::tag('p', s($response['error']), ['class' => 'mb-1']);
        $rawdetails = (!empty($response['raw']))
            ? html_writer::tag('pre', s($response['raw']), ['class' => 'bg-white p-2 border rounded small mt-2'])
            : '';
        echo html_writer::div($errormsg . $errorbody . $rawdetails, 'alert alert-danger shadow-sm mb-4');
    } else {
        $data = $response['data'];
        $resultados = $data['resultados'] ?? [];
        $metodoutilizado = $data['metodo'] ?? $metodo;
        $datosorigen = strtoupper($data['datos'] ?? $fuente);

        echo html_writer::tag(
            'h4',
            '🎯 ' . get_string('results_title', 'block_videorec') .
            ' <span class="badge bg-secondary fs-6 ms-2">' . count($resultados) . ' resultados</span>' .
            ' <span class="badge bg-info text-dark fs-6 ms-1">Fuente: ' . s($datosorigen) . '</span>' .
            ' <span class="badge bg-light text-secondary border fs-6 ms-1">Método: ' . s($metodoutilizado) . '</span>',
            ['class' => 'mb-3 mt-4']
        );

        if (empty($resultados)) {
            echo html_writer::div(
                html_writer::tag('p', get_string('no_results_found', 'block_videorec'), ['class' => 'text-muted mb-0']),
                'alert alert-warning text-center p-4'
            );
        } else {
            // Render results grid.
            echo '<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4 mb-5">';

            foreach ($resultados as $r) {
                $vid = s($r['id'] ?? '');
                $vtitle = s($r['titulo'] ?? '');
                $vcanal = s($r['canal'] ?? '');
                $vorigen = $r['origen'] ?? strtolower($datosorigen);
                $vpuntuacion = isset($r['puntuacion']) ? round($r['puntuacion'] * 100) : 0;
                $vurl = $r['url'] ?? '';
                $coincidencias = $r['coincidencias'] ?? [];

                $isyt = ($vorigen === 'youtube' && !empty($vid));
                $thumburl = $isyt ? "https://img.youtube.com/vi/{$vid}/hqdefault.jpg" : "";
                $embedurl = $isyt ? "https://www.youtube-nocookie.com/embed/{$vid}?autoplay=1" : "";

                // Card markup.
                echo '<div class="col">';
                echo '<div class="card h-100 shadow-sm border-0 position-relative" style="border-radius: 12px; overflow: hidden; background: #fff;">';

                // Thumbnail.
                if ($isyt) {
                    echo '<div class="position-relative bg-dark" style="height: 180px; overflow: hidden; cursor: pointer;" ' .
                         'onclick="abrirModalVideo(\'' . s($embedurl) . '\', \'' . addslashes($vtitle) . '\')">';
                    echo '<img src="' . s($thumburl) . '" alt="' . $vtitle . '" class="w-100 h-100" style="object-fit: cover;">';
                    echo '<div class="position-absolute top-50 start-50 translate-middle badge bg-danger rounded-pill px-3 py-2 fs-6 shadow">▶ ' . get_string('btn_play', 'block_videorec') . '</div>';
                    echo '</div>';
                } else {
                    echo '<div class="d-flex align-items-center justify-content-center bg-light text-muted border-bottom" style="height: 150px;">';
                    echo '<span class="fs-4">📚 ' . get_string('source_simulado', 'block_videorec') . '</span>';
                    echo '</div>';
                }

                // Card body.
                echo '<div class="card-body d-flex flex-column">';

                // Badges row.
                echo '<div class="d-flex justify-content-between align-items-center mb-2">';
                echo '<span class="badge bg-' . ($isyt ? 'danger' : 'secondary') . '">' . strtoupper($vorigen) . '</span>';
                echo '<span class="badge bg-primary fs-7">' . $vpuntuacion . '% ' . get_string('match_score', 'block_videorec') . '</span>';
                echo '</div>';

                // Title & Channel.
                echo '<h6 class="card-title fw-bold text-dark mb-1" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.5rem;">' . $vtitle . '</h6>';
                if (!empty($vcanal)) {
                    echo '<p class="small text-muted mb-2">📺 ' . $vcanal . '</p>';
                }

                // Matching terms.
                if (!empty($coincidencias)) {
                    echo '<div class="small text-muted mb-3">';
                    echo '<span class="me-1">' . get_string('matches_terms', 'block_videorec') . '</span>';
                    foreach ($coincidencias as $c) {
                        echo '<span class="badge bg-success-subtle text-success me-1">✓ ' . s($c) . '</span>';
                    }
                    echo '</div>';
                }

                // Action buttons.
                echo '<div class="mt-auto pt-2 d-flex gap-2">';
                if ($isyt) {
                    echo '<button type="button" class="btn btn-sm btn-danger flex-grow-1" ' .
                         'onclick="abrirModalVideo(\'' . s($embedurl) . '\', \'' . addslashes($vtitle) . '\')">▶ ' .
                         get_string('btn_play', 'block_videorec') . '</button>';
                    echo '<a href="' . s($vurl) . '" target="_blank" rel="noopener" class="btn btn-sm btn-outline-secondary">' .
                         get_string('btn_open_youtube', 'block_videorec') . '</a>';
                } else {
                    echo '<span class="small text-muted fst-italic py-1">' . get_string('simulated_notice', 'block_videorec') . '</span>';
                }
                echo '</div>'; // End actions

                echo '</div>'; // End card body
                echo '</div>'; // End card
                echo '</div>'; // End col
            }

            echo '</div>'; // End row
        }
    }
}

// Modal Video Player for YouTube.
?>
<div class="modal fade" id="videoModalPlayer" tabindex="-1" aria-labelledby="videoModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg modal-dialog-centered">
    <div class="modal-content shadow-lg border-0" style="border-radius: 14px; overflow: hidden;">
      <div class="modal-header bg-dark text-white py-2">
        <h6 class="modal-title text-truncate me-3" id="videoModalLabel">Reproductor de Video</h6>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close" onclick="cerrarModalVideo()"></button>
      </div>
      <div class="modal-body p-0 bg-black" style="position: relative; padding-bottom: 56.25% !important; height: 0;">
        <iframe id="videoIframePlayer" src="" style="position: absolute; top:0; left:0; width:100%; height:100%; border:0;" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div>
    </div>
  </div>
</div>

<script>
function abrirModalVideo(url, title) {
    const frame = document.getElementById('videoIframePlayer');
    const label = document.getElementById('videoModalLabel');
    frame.src = url;
    label.textContent = title;
    const modalEl = document.getElementById('videoModalPlayer');
    if (window.bootstrap && window.bootstrap.Modal) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    } else {
        modalEl.classList.add('show');
        modalEl.style.display = 'block';
    }
}

function cerrarModalVideo() {
    const frame = document.getElementById('videoIframePlayer');
    frame.src = '';
    const modalEl = document.getElementById('videoModalPlayer');
    if (window.bootstrap && window.bootstrap.Modal) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    } else {
        modalEl.classList.remove('show');
        modalEl.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const modalEl = document.getElementById('videoModalPlayer');
    modalEl.addEventListener('hidden.bs.modal', function() {
        cerrarModalVideo();
    });
});
</script>
<?php

// Return button.
$backurl = new moodle_url('/course/view.php', ['id' => $course->id]);
$backbutton = html_writer::link(
    $backurl,
    '← ' . get_string('back_to_course', 'block_videorec'),
    ['class' => 'btn btn-outline-secondary mt-3 mb-4']
);
echo html_writer::div($backbutton, 'mt-2 mb-4');

echo $OUTPUT->footer();
