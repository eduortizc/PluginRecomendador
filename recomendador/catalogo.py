"""
catalogo.py – Lectura y validación del catálogo de videos.

Carga el archivo JSON del catálogo y valida que cada registro
contenga los campos obligatorios del contrato de E1.
"""

import json
from pathlib import Path

# Campos obligatorios en cada registro del catálogo.
CAMPOS_REQUERIDOS = {"id", "titulo", "descripcion", "origen", "url"}


class ErrorCatalogo(Exception):
    """Error al leer o validar el catálogo de videos."""


def ruta_catalogo_default() -> Path:
    """Devuelve la ruta al catálogo de demostración relativa al proyecto."""
    return Path(__file__).resolve().parent.parent / "data" / "videos_demo.json"


def cargar_catalogo(ruta: Path | None = None) -> list[dict]:
    """Carga y valida el catálogo JSON.

    Parámetros
    ----------
    ruta : Path | None
        Ruta al archivo JSON.  Si es None usa el catálogo de demostración.

    Devuelve
    --------
    list[dict]
        Lista de candidatos validados.

    Lanza
    -----
    ErrorCatalogo
        Si el archivo no existe, no es JSON válido o los registros
        están incompletos.
    """
    if ruta is None:
        ruta = ruta_catalogo_default()

    if not ruta.exists():
        raise ErrorCatalogo(f"No se encontró el catálogo: {ruta}")

    try:
        contenido = ruta.read_text(encoding="utf-8")
        datos = json.loads(contenido)
    except json.JSONDecodeError as exc:
        raise ErrorCatalogo(f"El archivo no contiene JSON válido: {exc}") from exc

    if not isinstance(datos, dict) or "videos" not in datos:
        raise ErrorCatalogo(
            "El JSON debe contener un objeto con la clave 'videos'."
        )

    videos = datos["videos"]
    if not isinstance(videos, list) or len(videos) == 0:
        raise ErrorCatalogo("La lista de videos está vacía o no es una lista.")

    for i, video in enumerate(videos):
        faltantes = CAMPOS_REQUERIDOS - set(video.keys())
        if faltantes:
            raise ErrorCatalogo(
                f"Registro {i} ('{video.get('id', '?')}'): "
                f"faltan campos {sorted(faltantes)}."
            )

    return videos
