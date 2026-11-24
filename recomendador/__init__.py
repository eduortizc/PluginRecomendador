"""
Recomendador de videos educativos – prototipo independiente.

Etapa E1: catálogo simulado y coincidencia textual.
Etapa E2: recuperación de candidatos reales mediante YouTube Data API v3.
Etapa E3: análisis semántico con sentence-transformers.
Etapa E4: perfiles, contexto pedagógico e interacciones.
Etapa E5: vecinos de usuario y ranking semántico-colaborativo.
"""

from .catalogo import cargar_catalogo, ErrorCatalogo
from .ranking import normalizar, puntuar, recomendar
from .youtube import buscar_videos_youtube, ErrorYouTube, obtener_clave_api
from .semantico import ModeloEmbeddings
from .colaborativo import predecir_colaborativo
from .interacciones import (
    GestorInteracciones,
    ErrorInteraccion,
    TIPO_IMPRESION,
    TIPO_APERTURA,
    TIPO_SELECCION,
    TIPO_VALORACION,
    TIPOS_VALIDOS,
)

__all__ = [
    "cargar_catalogo",
    "ErrorCatalogo",
    "normalizar",
    "puntuar",
    "recomendar",
    "buscar_videos_youtube",
    "ErrorYouTube",
    "obtener_clave_api",
    "ModeloEmbeddings",
    "predecir_colaborativo",
    "GestorInteracciones",
    "ErrorInteraccion",
    "TIPO_IMPRESION",
    "TIPO_APERTURA",
    "TIPO_SELECCION",
    "TIPO_VALORACION",
    "TIPOS_VALIDOS",
]

