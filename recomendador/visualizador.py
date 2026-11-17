"""
visualizador.py – Generador de interfaz visual para las recomendaciones.

Genera una vista HTML moderna e interactiva sin dependencias externas,
mostrando miniaturas de YouTube, etiquetas de coincidencia, canal y reproductor.
"""

import html
import json
import webbrowser
from pathlib import Path


def renderizar_html(resultado: dict) -> str:
    """Genera el código HTML completo para visualizar un resultado de recomendación."""
    consulta = html.escape(resultado.get("consulta", ""))
    metodo = html.escape(resultado.get("metodo", "coincidencia_textual"))
    datos = html.escape(resultado.get("datos", "simulados"))
    terminos = resultado.get("terminos_utilizados", [])
    resultados = resultado.get("resultados", [])
    mensaje = html.escape(resultado.get("mensaje", ""))

    terminos_html = "".join(
        f'<span class="term-badge">{html.escape(t)}</span>' for t in terminos
    )

    cards_html = ""
    for r in resultados:
        vid_id = html.escape(str(r.get("id", "")))
        titulo = html.escape(r.get("titulo", "Sin título"))
        canal = html.escape(r.get("canal", "Canal no especificado"))
        origen = html.escape(r.get("origen", datos))
        puntuacion = r.get("puntuacion", 0.0)
        porcentaje = int(puntuacion * 100)
        coincidencias = r.get("coincidencias", [])
        url = r.get("url")

        # Miniatura de YouTube o placeholder educativo para simulados
        if origen == "youtube" and vid_id:
            thumb_url = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
            embed_url = f"https://www.youtube-nocookie.com/embed/{vid_id}?autoplay=1"
            action_btn = (
                f'<button class="btn-play" onclick="abrirModal(\'{embed_url}\', \'{titulo}\')">'
                f'▶ Reproducir aquí</button>'
                f'<a class="btn-link" href="https://www.youtube.com/watch?v={vid_id}" target="_blank" rel="noopener">'
                f'Abrir en YouTube ↗</a>'
            )
        else:
            thumb_url = ""
            action_btn = '<span class="sim-tag">Registro simulado (sin video en línea)</span>'

        coincidencias_chips = "".join(
            f'<span class="match-chip">✓ {html.escape(c)}</span>' for c in coincidencias
        )

        thumb_html = (
            f'<div class="card-thumb" style="background-image: url(\'{thumb_url}\');" onclick="abrirModal(\'{embed_url}\', \'{titulo}\')">'
            f'  <div class="thumb-overlay"><span class="play-icon">▶</span></div>'
            f'</div>'
            if thumb_url
            else '<div class="card-thumb simulated-thumb"><span>📚 Catálogo Simulado</span></div>'
        )

        cards_html += f"""
        <article class="video-card">
            {thumb_html}
            <div class="card-content">
                <div class="card-header">
                    <span class="source-badge {origen}">{origen.upper()}</span>
                    <span class="score-badge">{porcentaje}% coincidencia</span>
                </div>
                <h3 class="video-title">{titulo}</h3>
                <p class="channel-name">📺 {canal}</p>
                <div class="matches-list">
                    <span class="matches-label">Palabras encontradas:</span>
                    {coincidencias_chips}
                </div>
                <div class="card-actions">
                    {action_btn}
                </div>
            </div>
        </article>
        """

    if not cards_html:
        cards_html = f"""
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3>No se encontraron recomendaciones</h3>
            <p>{mensaje or 'Prueba con otros términos de búsqueda relacionados con la unidad de tu curso.'}</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recomendaciones para: {consulta}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.2);
            --danger: #ef4444;
            --success: #10b981;
            --border: #334155;
            --radius: 14px;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem 1.5rem;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            border: 1px solid var(--border);
            backdrop-filter: blur(12px);
            border-radius: var(--radius);
            padding: 1.8rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        .top-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        h1 {{
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }}
        .status-pill {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .query-box {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.9rem 1.2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.8rem;
        }}
        .query-text {{
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--accent);
        }}
        .terms-wrap {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        .term-badge {{
            background: var(--surface-hover);
            color: var(--text-muted);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.8rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
        }}
        .video-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        }}
        .video-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow: 0 12px 28px rgba(56, 189, 248, 0.12);
        }}
        .card-thumb {{
            width: 100%;
            height: 190px;
            background-size: cover;
            background-position: center;
            position: relative;
            cursor: pointer;
            background-color: #0b1120;
        }}
        .simulated-thumb {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            font-size: 1.1rem;
            font-weight: 500;
            cursor: default;
        }}
        .thumb-overlay {{
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease, background 0.2s ease;
        }}
        .card-thumb:hover .thumb-overlay {{
            opacity: 1;
            background: rgba(0, 0, 0, 0.55);
        }}
        .play-icon {{
            font-size: 2.4rem;
            color: white;
            background: rgba(239, 68, 68, 0.9);
            width: 56px;
            height: 56px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding-left: 4px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        }}
        .card-content {{
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            flex: 1;
            gap: 0.8rem;
        }}
        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
        }}
        .source-badge {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            padding: 0.25rem 0.55rem;
            border-radius: 6px;
        }}
        .source-badge.youtube {{
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}
        .source-badge.simulado, .source-badge.simulados {{
            background: rgba(148, 163, 184, 0.15);
            color: #94a3b8;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }}
        .score-badge {{
            font-size: 0.78rem;
            font-weight: 700;
            color: #38bdf8;
            background: var(--accent-glow);
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
        }}
        .video-title {{
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--text-main);
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.8rem;
        }}
        .channel-name {{
            font-size: 0.88rem;
            color: var(--text-muted);
            font-weight: 500;
        }}
        .matches-list {{
            background: rgba(15, 23, 42, 0.4);
            border-radius: 8px;
            padding: 0.6rem 0.8rem;
            font-size: 0.8rem;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.35rem;
        }}
        .matches-label {{
            color: var(--text-muted);
            margin-right: 0.2rem;
        }}
        .match-chip {{
            background: rgba(16, 185, 129, 0.18);
            color: #34d399;
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            font-weight: 600;
        }}
        .card-actions {{
            margin-top: auto;
            display: flex;
            gap: 0.6rem;
            padding-top: 0.6rem;
        }}
        .btn-play {{
            flex: 1;
            background: #ef4444;
            color: white;
            border: none;
            padding: 0.6rem 0.8rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.88rem;
            cursor: pointer;
            transition: background 0.2s ease;
        }}
        .btn-play:hover {{
            background: #dc2626;
        }}
        .btn-link {{
            background: var(--surface-hover);
            color: var(--text-main);
            text-decoration: none;
            padding: 0.6rem 0.8rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s ease;
        }}
        .btn-link:hover {{
            background: #475569;
        }}
        .sim-tag {{
            font-size: 0.82rem;
            color: var(--text-muted);
            font-style: italic;
        }}
        .empty-state {{
            grid-column: 1 / -1;
            background: var(--surface);
            border: 1px dashed var(--border);
            border-radius: var(--radius);
            padding: 3rem 1.5rem;
            text-align: center;
        }}
        .empty-icon {{
            font-size: 3rem;
            margin-bottom: 0.8rem;
        }}
        /* Modal Video Player */
        .modal-backdrop {{
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 1rem;
        }}
        .modal-window {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            width: 100%;
            max-width: 860px;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        }}
        .modal-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.9rem 1.2rem;
            border-bottom: 1px solid var(--border);
        }}
        .modal-title {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-main);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding-right: 1rem;
        }}
        .modal-close {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.6rem;
            cursor: pointer;
            line-height: 1;
        }}
        .modal-close:hover {{
            color: white;
        }}
        .video-wrapper {{
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            background: black;
        }}
        .video-wrapper iframe {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            border: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="top-row">
                <h1>🎓 Recomendador de Videos Educativos</h1>
                <span class="status-pill">Fuente activa: {datos.upper()}</span>
            </div>
            <div class="query-box">
                <div>
                    <span style="font-size: 0.82rem; color: var(--text-muted); display: block;">Tema consultado:</span>
                    <span class="query-text">"{consulta}"</span>
                </div>
                <div class="terms-wrap">
                    <span style="font-size: 0.82rem; color: var(--text-muted);">Términos clave:</span>
                    {terminos_html}
                </div>
            </div>
        </header>

        <main class="grid">
            {cards_html}
        </main>
    </div>

    <!-- Modal para reproducir video -->
    <div id="modalPlayer" class="modal-backdrop" onclick="cerrarModal(event)">
        <div class="modal-window" onclick="event.stopPropagation()">
            <div class="modal-header">
                <span id="modalVideoTitle" class="modal-title">Reproductor</span>
                <button class="modal-close" onclick="cerrarModal(null)">✕</button>
            </div>
            <div class="video-wrapper">
                <iframe id="modalIframe" src="" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
        </div>
    </div>

    <script>
        function abrirModal(embedUrl, titulo) {{
            const modal = document.getElementById('modalPlayer');
            const iframe = document.getElementById('modalIframe');
            const titleEl = document.getElementById('modalVideoTitle');
            iframe.src = embedUrl;
            titleEl.textContent = titulo;
            modal.style.display = 'flex';
        }}

        function cerrarModal(event) {{
            const modal = document.getElementById('modalPlayer');
            const iframe = document.getElementById('modalIframe');
            iframe.src = '';
            modal.style.display = 'none';
        }}

        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                cerrarModal(null);
            }}
        }});
    </script>
</body>
</html>
"""


def exportar_y_abrir(resultado: dict, ruta_archivo: Path | str | None = None) -> Path:
    """Genera el archivo HTML en disco y lo abre en el navegador predeterminado."""
    if ruta_archivo is None:
        ruta_archivo = Path(__file__).resolve().parent.parent / "recomendaciones.html"
    else:
        ruta_archivo = Path(ruta_archivo)

    contenido_html = renderizar_html(resultado)
    ruta_archivo.write_text(contenido_html, encoding="utf-8")

    webbrowser.open(ruta_archivo.resolve().as_uri())
    return ruta_archivo
