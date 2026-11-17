"""
servidor.py – Servidor web interactivo local para explorar recomendaciones.

Utiliza la biblioteca estándar de Python (http.server) para ofrecer una interfaz
web visual sin depender de servidores o frameworks externos.
Soporta los modos de ranking: textual, semántico e híbrido (E3),
así como perfiles de usuario, registro de valoraciones e interacciones (E4).
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
from pathlib import Path

from .catalogo import cargar_catalogo, ErrorCatalogo
from .ranking import recomendar
from .youtube import buscar_videos_youtube, ErrorYouTube
from .interacciones import GestorInteracciones, ErrorInteraccion

# Instancias compartidas en memoria para reutilizar entre peticiones
_modelo_embeddings = None
_gestor_interacciones = GestorInteracciones()


def _obtener_modelo():
    global _modelo_embeddings
    if _modelo_embeddings is None:
        from .semantico import ModeloEmbeddings
        _modelo_embeddings = ModeloEmbeddings()
    return _modelo_embeddings


def _obtener_interfaz_web_html() -> str:
    """Devuelve el HTML/CSS/JS de la aplicación interactiva local."""
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Explorador Visual – Recomendador de Videos Educativos</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --surface: #131c2e;
            --surface-hover: #1e2c45;
            --surface-card: #152238;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.25);
            --danger: #ef4444;
            --success: #10b981;
            --border: #243552;
            --radius: 14px;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem 1.5rem;
            line-height: 1.5;
        }
        .container {
            max-width: 1140px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 2rem;
        }
        h1 {
            font-size: 2.1rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 40%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: var(--text-muted);
            font-size: 1.05rem;
        }
        .search-panel {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 2.5rem;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
        }
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }
        .input-group {
            display: flex;
            gap: 0.8rem;
        }
        .search-input {
            flex: 1;
            background: #0d1524;
            border: 1px solid var(--border);
            color: white;
            font-family: inherit;
            font-size: 1.05rem;
            padding: 0.85rem 1.2rem;
            border-radius: 10px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .search-input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }
        .btn-search {
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: white;
            border: none;
            padding: 0 1.8rem;
            border-radius: 10px;
            font-family: inherit;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.15s, opacity 0.15s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .btn-search:hover {
            opacity: 0.95;
            transform: translateY(-1px);
        }
        .options-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            font-size: 0.9rem;
            color: var(--text-muted);
        }
        .source-selector {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            background: #0d1524;
            padding: 0.35rem 0.5rem;
            border-radius: 8px;
            border: 1px solid var(--border);
        }
        .source-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            padding: 0.4rem 0.9rem;
            border-radius: 6px;
            font-family: inherit;
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .source-btn.active {
            background: #38bdf8;
            color: #0b1120;
        }
        .select-user {
            background: #0d1524;
            color: #f8fafc;
            border: 1px solid var(--border);
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            font-family: inherit;
            font-size: 0.88rem;
            outline: none;
        }
        .presets {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        .preset-chip {
            background: var(--surface-hover);
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .preset-chip:hover {
            color: white;
            border-color: var(--accent);
        }
        .results-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.2rem;
            padding-bottom: 0.8rem;
            border-bottom: 1px solid var(--border);
        }
        .results-title {
            font-size: 1.25rem;
            font-weight: 600;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
            gap: 1.5rem;
        }
        .video-card {
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }
        .video-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow: 0 10px 25px rgba(56, 189, 248, 0.12);
        }
        .card-thumb {
            width: 100%;
            height: 195px;
            background-size: cover;
            background-position: center;
            position: relative;
            cursor: pointer;
            background-color: #070b14;
        }
        .thumb-overlay {
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        .card-thumb:hover .thumb-overlay {
            opacity: 1;
            background: rgba(0, 0, 0, 0.55);
        }
        .play-icon {
            font-size: 2.2rem;
            color: white;
            background: #ef4444;
            width: 52px;
            height: 52px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding-left: 3px;
        }
        .card-body {
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            flex: 1;
            gap: 0.75rem;
        }
        .badges-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .source-tag {
            font-size: 0.72rem;
            font-weight: 700;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
        }
        .source-tag.youtube {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.35);
        }
        .source-tag.simulado {
            background: rgba(148, 163, 184, 0.2);
            color: #94a3b8;
            border: 1px solid rgba(148, 163, 184, 0.35);
        }
        .score-tag {
            font-size: 0.8rem;
            font-weight: 700;
            color: #38bdf8;
            background: var(--accent-glow);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
        }
        .card-title {
            font-size: 1.05rem;
            font-weight: 600;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.8rem;
        }
        .card-channel {
            font-size: 0.88rem;
            color: var(--text-muted);
        }
        .card-matches {
            background: #090e18;
            border-radius: 6px;
            padding: 0.5rem 0.7rem;
            font-size: 0.78rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            align-items: center;
        }
        .match-badge {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            padding: 0.12rem 0.45rem;
            border-radius: 4px;
            font-weight: 600;
        }
        /* Valoración de estrellas (E4) */
        .rating-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.4rem 0.6rem;
            background: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
            border: 1px solid var(--border);
            font-size: 0.8rem;
        }
        .stars-wrap {
            display: inline-flex;
            gap: 0.2rem;
            cursor: pointer;
        }
        .star-item {
            color: #64748b;
            font-size: 1.1rem;
            transition: color 0.15s;
        }
        .star-item:hover, .star-item.active {
            color: #fbbf24;
        }
        .rate-feedback {
            font-size: 0.72rem;
            color: #10b981;
            font-weight: 600;
        }
        .card-footer {
            margin-top: auto;
            display: flex;
            gap: 0.6rem;
            padding-top: 0.4rem;
        }
        .btn-modal {
            flex: 1;
            background: #ef4444;
            color: white;
            border: none;
            padding: 0.55rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
        }
        .btn-modal:hover { background: #dc2626; }
        .btn-ext {
            background: var(--surface-hover);
            color: var(--text);
            text-decoration: none;
            padding: 0.55rem 0.8rem;
            border-radius: 8px;
            font-size: 0.85rem;
            display: inline-flex;
            align-items: center;
        }
        .btn-ext:hover { background: #334155; }
        /* Modal Player */
        .modal-backdrop {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 1rem;
        }
        .modal-window {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            width: 100%;
            max-width: 860px;
            overflow: hidden;
        }
        .modal-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.8rem 1.2rem;
            border-bottom: 1px solid var(--border);
        }
        .modal-title {
            font-size: 0.95rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding-right: 1rem;
        }
        .modal-close {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.5rem;
            cursor: pointer;
        }
        .video-box {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            background: black;
        }
        .video-box iframe {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            border: none;
        }
        .loading {
            text-align: center;
            padding: 3rem;
            color: var(--text-muted);
            font-size: 1.1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Recomendador de Videos Educativos</h1>
            <p class="subtitle">Explora candidatos de YouTube o catálogo simulado con similitud textual, semántica e interacciones (E1-E4)</p>
        </header>

        <section class="search-panel">
            <form class="search-form" id="searchForm" onsubmit="realizarBusqueda(event)">
                <div class="input-group">
                    <input type="text" id="inputTema" class="search-input" placeholder="Escribe el tema o unidad del curso (ej: bases de datos relacionales)..." required autocomplete="off" value="bases de datos relacionales">
                    <button type="submit" class="btn-search">
                        <span>🔍 Recomendar</span>
                    </button>
                </div>

                <div class="options-row">
                    <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;">
                        <span>Fuente:</span>
                        <div class="source-selector">
                            <button type="button" id="btnYouTube" class="source-btn active" onclick="cambiarFuente('youtube')">YouTube (Real)</button>
                            <button type="button" id="btnSimulado" class="source-btn" onclick="cambiarFuente('simulado')">Simulado (Demo)</button>
                        </div>
                        <span style="margin-left:0.5rem;">Método:</span>
                        <div class="source-selector">
                            <button type="button" id="btnTextual" class="source-btn active" onclick="cambiarMetodo('textual')">Textual</button>
                            <button type="button" id="btnSemantico" class="source-btn" onclick="cambiarMetodo('semantico')">Semántico ✨</button>
                            <button type="button" id="btnHibrido" class="source-btn" onclick="cambiarMetodo('hibrido')">Híbrido</button>
                        </div>
                        <span style="margin-left:0.5rem;">👤 Usuario:</span>
                        <select id="selectUsuario" class="select-user">
                            <option value="usr_estudiante_01">Estudiante Principiante (usr_estudiante_01)</option>
                            <option value="usr_estudiante_02">Estudiante Avanzado (usr_estudiante_02)</option>
                            <option value="usr_estudiante_03">Estudiante Redes (usr_estudiante_03)</option>
                            <option value="usr_docente_01">Docente Titular BD (usr_docente_01)</option>
                        </select>
                    </div>

                    <div class="presets">
                        <span>Sugerencias:</span>
                        <span class="preset-chip" onclick="usarSugerencia('programacion orientada a objetos python')">Python POO</span>
                        <span class="preset-chip" onclick="usarSugerencia('consultas sql avanzadas')">SQL Avanzado</span>
                        <span class="preset-chip" onclick="usarSugerencia('estructuras de datos listas y arboles')">Árboles y Listas</span>
                        <span class="preset-chip" onclick="usarSugerencia('redes computadoras tcp ip')">Redes TCP/IP</span>
                    </div>
                </div>
            </form>
        </section>

        <div class="results-header" id="resultsHeader" style="display: none;">
            <h2 class="results-title" id="resultsTitle">Resultados recomendados</h2>
            <span id="resultsCount" style="color: var(--text-muted); font-size: 0.9rem;"></span>
        </div>

        <div id="resultsGrid" class="grid"></div>
    </div>

    <!-- Modal Player -->
    <div id="modalPlayer" class="modal-backdrop" onclick="cerrarModal(event)">
        <div class="modal-window" onclick="event.stopPropagation()">
            <div class="modal-top">
                <span id="modalTitle" class="modal-title">Reproductor</span>
                <button class="modal-close" onclick="cerrarModal(null)">✕</button>
            </div>
            <div class="video-box">
                <iframe id="modalFrame" src="" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
        </div>
    </div>

    <script>
        let fuenteActual = 'youtube';
        let metodoActual = 'textual';

        function cambiarFuente(fuente) {
            fuenteActual = fuente;
            document.getElementById('btnYouTube').classList.toggle('active', fuente === 'youtube');
            document.getElementById('btnSimulado').classList.toggle('active', fuente === 'simulado');
        }

        function cambiarMetodo(metodo) {
            metodoActual = metodo;
            document.getElementById('btnTextual').classList.toggle('active', metodo === 'textual');
            document.getElementById('btnSemantico').classList.toggle('active', metodo === 'semantico');
            document.getElementById('btnHibrido').classList.toggle('active', metodo === 'hibrido');
        }

        function usarSugerencia(tema) {
            document.getElementById('inputTema').value = tema;
            realizarBusqueda();
        }

        function obtenerUsuarioActivo() {
            return document.getElementById('selectUsuario').value || 'usr_estudiante_01';
        }

        async function registrarInteraccion(videoId, tipo, valor = null) {
            const usuarioId = obtenerUsuarioActivo();
            const tema = document.getElementById('inputTema').value.trim();
            try {
                const params = new URLSearchParams({
                    usuario_id: usuarioId,
                    video_id: videoId,
                    tipo: tipo,
                    tema: tema
                });
                if (valor !== null) params.append('valor', valor);
                await fetch(`/api/interaccion?${params.toString()}`);
            } catch (err) {
                console.error("Error al registrar interacción:", err);
            }
        }

        async function valorarVideo(videoId, estrellas) {
            await registrarInteraccion(videoId, 'valoracion', estrellas);
            const feedbackEl = document.getElementById(`feedback-${videoId}`);
            if (feedbackEl) {
                feedbackEl.textContent = `★ ${estrellas}.0 registrada`;
            }
            // Actualizar estilo de estrellas
            for (let i = 1; i <= 5; i++) {
                const star = document.getElementById(`star-${videoId}-${i}`);
                if (star) {
                    star.classList.toggle('active', i <= estrellas);
                }
            }
        }

        async function realizarBusqueda(e) {
            if (e) e.preventDefault();
            const tema = document.getElementById('inputTema').value.trim();
            if (!tema) return;

            const grid = document.getElementById('resultsGrid');
            const header = document.getElementById('resultsHeader');
            const count = document.getElementById('resultsCount');
            const usuarioId = obtenerUsuarioActivo();

            const msgCarga = metodoActual === 'textual'
                ? 'Buscando candidatos y calculando coincidencias...'
                : `Cargando modelo semántico y calculando similitud (método: ${metodoActual})...`;
            grid.innerHTML = `<div class="loading">${msgCarga}</div>`;
            header.style.display = 'flex';

            try {
                const resp = await fetch(`/api/recomendar?tema=${encodeURIComponent(tema)}&fuente=${fuenteActual}&metodo=${metodoActual}&usuario_id=${encodeURIComponent(usuarioId)}&limite=5`);
                const data = await resp.json();

                if (!resp.ok || data.error) {
                    grid.innerHTML = `<div class="loading" style="color: #ef4444;">Error: ${data.error || 'No se pudo obtener la recomendación'}</div>`;
                    return;
                }

                renderizarResultados(data);
            } catch (err) {
                grid.innerHTML = `<div class="loading" style="color: #ef4444;">Error de conexión con el recomendador: ${err.message}</div>`;
            }
        }

        function renderizarResultados(data) {
            const grid = document.getElementById('resultsGrid');
            const count = document.getElementById('resultsCount');
            const resultados = data.resultados || [];

            count.textContent = `${resultados.length} recomendaciones encontradas (Fuente: ${data.datos}, Método: ${data.metodo})`;

            if (resultados.length === 0) {
                grid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 3rem; background: var(--surface); border-radius: var(--radius);">
                        <h3>Sin coincidencias</h3>
                        <p style="color: var(--text-muted); margin-top: 0.5rem;">${data.mensaje || 'No se encontraron videos con términos coincidentes.'}</p>
                    </div>`;
                return;
            }

            grid.innerHTML = resultados.map(r => {
                const porcentaje = Math.round(r.puntuacion * 100);
                const esYT = r.origen === 'youtube';
                const thumb = esYT 
                    ? `https://img.youtube.com/vi/${r.id}/hqdefault.jpg`
                    : '';
                const embedUrl = esYT ? `https://www.youtube-nocookie.com/embed/${r.id}?autoplay=1` : '';

                const chips = (r.coincidencias || []).map(c => `<span class="match-badge">✓ ${c}</span>`).join('');

                const thumbHtml = esYT
                    ? `<div class="card-thumb" style="background-image: url('${thumb}');" onclick="abrirModal('${embedUrl}', '${r.titulo.replace(/'/g, "\\'")}', '${r.id}')">
                         <div class="thumb-overlay"><span class="play-icon">▶</span></div>
                       </div>`
                    : `<div class="card-thumb" style="display:flex;align-items:center;justify-content:center;color:var(--text-muted);cursor:default;">📚 Catálogo Simulado</div>`;

                const btnModal = esYT
                    ? `<button class="btn-modal" onclick="abrirModal('${embedUrl}', '${r.titulo.replace(/'/g, "\\'")}', '${r.id}')">▶ Reproducir</button>
                       <a class="btn-ext" href="${r.url}" target="_blank" rel="noopener">YouTube ↗</a>`
                    : `<span style="font-size: 0.8rem; color: var(--text-muted); font-style: italic;">Sin video en línea</span>`;

                return `
                <article class="video-card">
                    ${thumbHtml}
                    <div class="card-body">
                        <div class="badges-row">
                            <span class="source-tag ${r.origen || data.datos}">${(r.origen || data.datos).toUpperCase()}</span>
                            <span class="score-tag">${porcentaje}% coincidencia</span>
                        </div>
                        <h3 class="card-title">${r.titulo}</h3>
                        <p class="card-channel">📺 ${r.canal || 'Sin canal especificado'}</p>
                        <div class="card-matches">
                            <span style="color: var(--text-muted); margin-right: 0.2rem;">Coincidencias:</span>
                            ${chips}
                        </div>
                        <div class="rating-row">
                            <span>Valorar:</span>
                            <div class="stars-wrap">
                                <span id="star-${r.id}-1" class="star-item" onclick="valorarVideo('${r.id}', 1)">★</span>
                                <span id="star-${r.id}-2" class="star-item" onclick="valorarVideo('${r.id}', 2)">★</span>
                                <span id="star-${r.id}-3" class="star-item" onclick="valorarVideo('${r.id}', 3)">★</span>
                                <span id="star-${r.id}-4" class="star-item" onclick="valorarVideo('${r.id}', 4)">★</span>
                                <span id="star-${r.id}-5" class="star-item" onclick="valorarVideo('${r.id}', 5)">★</span>
                            </div>
                            <span id="feedback-${r.id}" class="rate-feedback"></span>
                        </div>
                        <div class="card-footer">
                            ${btnModal}
                        </div>
                    </div>
                </article>`;
            }).join('');
        }

        function abrirModal(url, titulo, videoId) {
            if (videoId) {
                registrarInteraccion(videoId, 'apertura');
            }
            const modal = document.getElementById('modalPlayer');
            const frame = document.getElementById('modalFrame');
            const title = document.getElementById('modalTitle');
            frame.src = url;
            title.textContent = titulo;
            modal.style.display = 'flex';
        }

        function cerrarModal() {
            const modal = document.getElementById('modalPlayer');
            const frame = document.getElementById('modalFrame');
            frame.src = '';
            modal.style.display = 'none';
        }

        document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrarModal(); });

        window.addEventListener('DOMContentLoaded', () => { realizarBusqueda(); });
    </script>
</body>
</html>
"""


class _ManejadorRecomendador(BaseHTTPRequestHandler):
    """Manejador HTTP para la interfaz web, API de recomendación y API de interacciones."""

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)

        if url_parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_obtener_interfaz_web_html().encode("utf-8"))
            return

        if url_parsed.path == "/api/usuarios":
            usuarios = _gestor_interacciones.obtener_usuarios()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"usuarios": usuarios}, ensure_ascii=False).encode("utf-8"))
            return

        if url_parsed.path == "/api/matriz":
            matriz = _gestor_interacciones.generar_matriz_utilidad()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"matriz": matriz}, ensure_ascii=False).encode("utf-8"))
            return

        if url_parsed.path == "/api/interaccion":
            params = urllib.parse.parse_qs(url_parsed.query)
            usuario_id = params.get("usuario_id", [""])[0].strip()
            video_id = params.get("video_id", [""])[0].strip()
            tipo = params.get("tipo", ["apertura"])[0].strip()
            valor = params.get("valor", [None])[0]
            tema = params.get("tema", [""])[0].strip()

            try:
                evento = _gestor_interacciones.registrar_evento(
                    usuario_id=usuario_id,
                    video_id=video_id,
                    tipo=tipo,
                    valor=valor,
                    contexto={"tema": tema} if tema else None,
                )
                _gestor_interacciones.guardar()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "evento": evento}).encode("utf-8"))
            except ErrorInteraccion as exc:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        if url_parsed.path == "/api/recomendar":
            params = urllib.parse.parse_qs(url_parsed.query)
            tema = params.get("tema", [""])[0].strip()
            fuente = params.get("fuente", ["youtube"])[0].strip()
            metodo = params.get("metodo", ["textual"])[0].strip()
            usuario_id = params.get("usuario_id", [""])[0].strip()
            if metodo not in ("textual", "semantico", "hibrido"):
                metodo = "textual"
            limite = int(params.get("limite", ["5"])[0])
            limite = max(1, min(limite, 5))

            if not tema:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "El tema no puede estar vacío"}).encode("utf-8"))
                return

            if fuente == "youtube":
                try:
                    candidatos = buscar_videos_youtube(tema=tema, max_resultados=10)
                except ErrorYouTube as exc:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"Error YouTube API: {exc}"}).encode("utf-8"))
                    return
            else:
                try:
                    candidatos = cargar_catalogo()
                except ErrorCatalogo as exc:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"Error catálogo: {exc}"}).encode("utf-8"))
                    return

            modelo = None
            if metodo in ("semantico", "hibrido"):
                try:
                    modelo = _obtener_modelo()
                except ImportError as exc:
                    self.send_response(503)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
                    return

            contexto = {"usuario_id": usuario_id} if usuario_id else None
            resultado = recomendar(tema, candidatos, limite, metodo=metodo, modelo_embeddings=modelo, contexto=contexto)

            # Si hay usuario identificado, registrar evento de impresion para cada resultado
            if usuario_id:
                try:
                    for r in resultado.get("resultados", []):
                        _gestor_interacciones.registrar_evento(
                            usuario_id=usuario_id,
                            video_id=r["id"],
                            tipo="impresion",
                            contexto={"tema": tema},
                        )
                    _gestor_interacciones.guardar()
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(resultado, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def iniciar_servidor_web(puerto: int = 8080) -> None:
    """Inicia el servidor web local y abre la vista en el navegador."""
    direccion = ("127.0.0.1", puerto)
    servidor = HTTPServer(direccion, _ManejadorRecomendador)
    url = f"http://127.0.0.1:{puerto}"
    print(f"\n=======================================================")
    print(f"  🎓 Explorador Visual del Recomendador de Videos (E1-E4)")
    print(f"  Servidor activo en: {url}")
    print(f"  Presiona Ctrl+C en la terminal para detenerlo")
    print(f"=======================================================\n")
    webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        servidor.server_close()
