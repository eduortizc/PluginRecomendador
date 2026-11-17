"""
youtube.py – Recuperación de candidatos reales mediante YouTube Data API v3.

Permite consultar la API oficial de YouTube para obtener candidatos de video
con metadatos reales (id, título, descripción, canal, fecha, URL, vistas,
likes y duración), manejando errores de red, cuotas, claves y respuestas vacías.
"""

import html
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


class ErrorYouTube(Exception):
    """Excepción para errores al interactuar con YouTube Data API."""

    def __init__(self, mensaje: str, codigo: str = "error_desconocido") -> None:
        super().__init__(mensaje)
        self.codigo = codigo


def _ruta_raiz_proyecto() -> Path:
    """Devuelve la ruta raíz del proyecto Recomendador_Ext."""
    return Path(__file__).resolve().parent.parent


def obtener_clave_api(ruta_env: Path | None = None) -> str:
    """Obtiene la clave de API de YouTube.

    Prioridad de búsqueda:
    1. Variable de entorno YOUTUBE_API_KEY.
    2. Archivo .env en la raíz del proyecto.

    Devuelve
    --------
    str
        Clave de API válida.

    Lanza
    -----
    ErrorYouTube
        Si no se encuentra ninguna clave configurada.
    """
    # 1. Variable de entorno explícita
    clave_env = os.environ.get("YOUTUBE_API_KEY")
    if clave_env and clave_env.strip():
        return clave_env.strip()

    # 2. Archivo .env
    if ruta_env is None:
        ruta_env = _ruta_raiz_proyecto() / ".env"

    if ruta_env.exists():
        try:
            lineas = ruta_env.read_text(encoding="utf-8").splitlines()
            for linea in lineas:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                # Formato estándar: CLAVE=VALOR
                if "=" in linea:
                    nombre, valor = linea.split("=", 1)
                    if "API_KEY" in nombre.upper():
                        val_limpio = valor.split("//")[0].split("#")[0].strip().strip("\"'")
                        if val_limpio:
                            return val_limpio
                # Formato directo: AIza... // comentario
                elif linea.startswith("AIza"):
                    val_limpio = linea.split("//")[0].split("#")[0].strip()
                    if val_limpio:
                        return val_limpio
        except OSError as exc:
            raise ErrorYouTube(
                f"No se pudo leer el archivo .env: {exc}",
                codigo="error_lectura_env",
            ) from exc

    raise ErrorYouTube(
        "No se encontró la clave de API de YouTube. Configura YOUTUBE_API_KEY en las "
        "variables de entorno o define la clave en el archivo .env.",
        codigo="clave_no_encontrada",
    )


def _parsear_duracion_iso8601(duracion_iso: str) -> tuple[str, int]:
    """Convierte duración ISO 8601 (PT1H2M3S) a formato legible y segundos.

    Parámetros
    ----------
    duracion_iso : str
        Duración en formato ISO 8601 (ej: "PT12M45S", "PT1H2M3S", "PT30S").

    Devuelve
    --------
    tuple[str, int]
        (cadena legible como "12:45" o "1:02:03", total en segundos)
    """
    if not duracion_iso:
        return ("0:00", 0)

    patron = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
    match = patron.match(duracion_iso)
    if not match:
        return ("0:00", 0)

    horas = int(match.group(1) or 0)
    minutos = int(match.group(2) or 0)
    segundos = int(match.group(3) or 0)

    total_segundos = horas * 3600 + minutos * 60 + segundos

    if horas > 0:
        texto = f"{horas}:{minutos:02d}:{segundos:02d}"
    else:
        texto = f"{minutos}:{segundos:02d}"

    return (texto, total_segundos)


def _enriquecer_con_estadisticas(
    candidatos: list[dict],
    api_key: str,
    timeout: int = 10,
) -> list[dict]:
    """Enriquece candidatos con estadísticas y duración desde videos.list.

    Realiza una sola llamada a videos.list con los IDs de los candidatos
    (hasta 50 por lote), que cuesta 1 unidad de cuota de la API.

    Nota: Las vistas y likes son señales de popularidad, NO constituyen
    filtrado colaborativo. Se documentan como tal en la tesis.

    Parámetros
    ----------
    candidatos : list[dict]
        Lista de candidatos obtenidos de search.list.
    api_key : str
        Clave de la API de YouTube.
    timeout : int
        Tiempo límite en segundos.

    Devuelve
    --------
    list[dict]
        Los mismos candidatos enriquecidos con vistas, likes y duración.
    """
    if not candidatos:
        return candidatos

    # Recolectar IDs de video (máximo 50 por llamada)
    ids_video = [c["id"] for c in candidatos if c.get("id")]
    if not ids_video:
        return candidatos

    ids_lote = ids_video[:50]

    parametros = {
        "part": "statistics,contentDetails",
        "id": ",".join(ids_lote),
        "key": api_key,
    }

    url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(parametros)

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "RecomendadorExt/0.3 (Educativo)"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as respuesta:
            cuerpo = respuesta.read().decode("utf-8")
            datos = json.loads(cuerpo)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        # Si falla el enriquecimiento, devolver candidatos sin stats.
        # La búsqueda principal ya fue exitosa; no queremos perderla.
        for c in candidatos:
            c.setdefault("vistas", None)
            c.setdefault("likes", None)
            c.setdefault("duracion", None)
            c.setdefault("duracion_segundos", None)
        return candidatos

    # Mapear ID -> estadísticas
    stats_por_id: dict[str, dict] = {}
    for item in datos.get("items", []):
        vid = item.get("id", "")
        estadisticas = item.get("statistics", {})
        detalles = item.get("contentDetails", {})

        duracion_iso = detalles.get("duration", "")
        duracion_texto, duracion_seg = _parsear_duracion_iso8601(duracion_iso)

        stats_por_id[vid] = {
            "vistas": int(estadisticas.get("viewCount", 0)),
            "likes": int(estadisticas.get("likeCount", 0)),
            "duracion": duracion_texto,
            "duracion_segundos": duracion_seg,
        }

    # Aplicar stats a cada candidato
    for c in candidatos:
        vid = c.get("id", "")
        if vid in stats_por_id:
            c.update(stats_por_id[vid])
        else:
            c["vistas"] = None
            c["likes"] = None
            c["duracion"] = None
            c["duracion_segundos"] = None

    return candidatos


def buscar_videos_youtube(
    tema: str,
    max_resultados: int = 10,
    api_key: str | None = None,
    idioma: str = "es",
    timeout: int = 10,
    enriquecer: bool = True,
) -> list[dict]:
    """Recupera candidatos de video desde YouTube Data API v3.

    Parámetros
    ----------
    tema : str
        Tema o consulta de búsqueda.
    max_resultados : int
        Cantidad máxima de videos a solicitar (1 a 50, por defecto 10).
    api_key : str | None
        Clave de la API. Si es None, se obtiene mediante obtener_clave_api().
    idioma : str
        Código de idioma preferido (por defecto 'es').
    timeout : int
        Tiempo límite de espera en segundos para la conexión HTTP.
    enriquecer : bool
        Si True (defecto), realiza una segunda llamada a videos.list para
        obtener vistas, likes y duración. Cuesta 1 unidad de cuota adicional.

    Devuelve
    --------
    list[dict]
        Lista de candidatos con id, titulo, descripcion, canal, publicado_el,
        origen ('youtube'), url, y opcionalmente vistas, likes, duracion,
        duracion_segundos.

    Lanza
    -----
    ValueError
        Si el tema está vacío.
    ErrorYouTube
        En caso de errores de autenticación, cuotas, conectividad o servicio.
    """
    tema_limpio = tema.strip()
    if not tema_limpio:
        raise ValueError("El tema de búsqueda no puede estar vacío.")

    if api_key is None:
        api_key = obtener_clave_api()

    limite_seguro = max(1, min(max_resultados, 50))

    parametros = {
        "part": "snippet",
        "q": tema_limpio,
        "type": "video",
        "maxResults": str(limite_seguro),
        "relevanceLanguage": idioma,
        "safeSearch": "moderate",
        "key": api_key,
    }

    url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(parametros)

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "RecomendadorExt/0.3 (Educativo)"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as respuesta:
            cuerpo = respuesta.read().decode("utf-8")
            datos = json.loads(cuerpo)
    except urllib.error.HTTPError as exc:
        cuerpo_error = exc.read().decode("utf-8", errors="replace")
        mensaje_detalle = ""
        motivo = "error_http"

        try:
            error_json = json.loads(cuerpo_error)
            errores = error_json.get("error", {}).get("errors", [])
            if errores:
                motivo = errores[0].get("reason", "error_http")
                mensaje_detalle = errores[0].get("message", "")
        except json.JSONDecodeError:
            mensaje_detalle = cuerpo_error[:200]

        if exc.code == 403:
            if motivo == "quotaExceeded":
                raise ErrorYouTube(
                    "Cuota diaria de YouTube Data API excedida.",
                    codigo="cuota_excedida",
                ) from exc
            raise ErrorYouTube(
                f"Acceso denegado a YouTube Data API: {mensaje_detalle or 'permisos insuficientes o clave no autorizada.'}",
                codigo="acceso_denegado",
            ) from exc

        if exc.code == 400:
            raise ErrorYouTube(
                f"Petición inválida a YouTube Data API: {mensaje_detalle or 'parámetros o clave incorrectos.'}",
                codigo="peticion_invalida",
            ) from exc

        if 500 <= exc.code < 600:
            raise ErrorYouTube(
                "El servicio de YouTube Data API no está disponible en este momento (error 5xx).",
                codigo="servicio_no_disponible",
            ) from exc

        raise ErrorYouTube(
            f"Error HTTP {exc.code} de YouTube Data API: {mensaje_detalle}",
            codigo="error_http",
        ) from exc

    except urllib.error.URLError as exc:
        raise ErrorYouTube(
            f"No se pudo conectar con YouTube Data API (error de red): {exc.reason}",
            codigo="error_red",
        ) from exc

    except TimeoutError as exc:
        raise ErrorYouTube(
            "Tiempo de espera agotado al conectar con YouTube Data API.",
            codigo="tiempo_agotado",
        ) from exc

    except json.JSONDecodeError as exc:
        raise ErrorYouTube(
            f"Respuesta inesperada de YouTube (no es JSON válido): {exc}",
            codigo="json_invalido",
        ) from exc

    items = datos.get("items", [])
    candidatos: list[dict] = []

    for item in items:
        id_obj = item.get("id", {})
        video_id = id_obj.get("videoId")
        if not video_id:
            continue

        snippet = item.get("snippet", {})
        titulo = html.unescape(snippet.get("title", ""))
        descripcion = html.unescape(snippet.get("description", ""))
        canal = html.unescape(snippet.get("channelTitle", ""))
        publicado_el = snippet.get("publishedAt", "")

        candidatos.append({
            "id": video_id,
            "titulo": titulo,
            "descripcion": descripcion,
            "canal": canal,
            "publicado_el": publicado_el,
            "origen": "youtube",
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })

    # Enriquecer con estadísticas (vistas, likes, duración)
    if enriquecer and candidatos:
        candidatos = _enriquecer_con_estadisticas(candidatos, api_key, timeout)

    return candidatos
