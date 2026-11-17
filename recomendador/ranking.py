"""
ranking.py – Función de puntuación por coincidencia textual, semántica e híbrida.

Modos disponibles
-----------------
textual   – Proporción de términos de la consulta presentes en el candidato (E1).
semantico – Similitud de coseno con embeddings de sentence-transformers (E3).
hibrido   – Combinación ponderada de textual y semántico (alpha·textual + (1-alpha)·semantico).

Soporta contexto pedagógico opcional (nivel, disciplina, rol de usuario) para
enriquecer las recomendaciones (E4).
"""

import unicodedata
import re

# ── Palabras funcionales ────────────────────────────────────────────
PALABRAS_EXCLUIDAS: set[str] = {
    "a", "al", "con", "de", "del", "e", "el", "en", "es", "la", "las",
    "lo", "los", "o", "para", "por", "que", "se", "su", "un", "una",
    "y", "como", "mas", "ni", "sin", "sobre",
}

# Umbral mínimo de similitud semántica para incluir un candidato
UMBRAL_SEMANTICO: float = 0.15


# ── Normalización ──────────────────────────────────────────────────

def _quitar_acentos(texto: str) -> str:
    """Elimina marcas diacríticas (acentos) conservando la letra base."""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def normalizar(texto: str) -> list[str]:
    """Convierte *texto* en una lista de palabras normalizadas."""
    texto = _quitar_acentos(texto.lower())
    palabras = re.findall(r"[a-z0-9]+", texto)
    return [p for p in palabras if p not in PALABRAS_EXCLUIDAS]


# ── Puntuación textual ─────────────────────────────────────────────

def puntuar(consulta_terms: list[str], candidato: dict) -> tuple[float, list[str]]:
    """Calcula la puntuación de un candidato respecto a la consulta."""
    if not consulta_terms:
        return 0.0, []

    texto_candidato = (
        candidato.get("titulo", "") + " " + candidato.get("descripcion", "")
    )
    tokens_candidato = set(normalizar(texto_candidato))

    consulta_unicos = set(consulta_terms)
    coincidentes_unicos = [t for t in consulta_unicos if t in tokens_candidato]
    puntuacion = len(coincidentes_unicos) / len(consulta_unicos)

    return puntuacion, sorted(coincidentes_unicos)


# ── Helpers internos ───────────────────────────────────────────────

def _datos_origen(candidatos: list[dict]) -> str:
    """Infiere la fuente de los candidatos ('youtube' o 'simulados')."""
    return "youtube" if any(c.get("origen") == "youtube" for c in candidatos) else "simulados"


def _item_base(cand: dict) -> dict:
    """Construye el dict base de un resultado preservando campos opcionales."""
    item: dict = {
        "id": cand["id"],
        "titulo": cand["titulo"],
    }
    for campo in ("url", "canal", "origen", "descripcion", "publicado_el",
                  "vistas", "likes", "duracion", "duracion_segundos"):
        if campo in cand:
            item[campo] = cand[campo]
    return item


# ── Función principal ──────────────────────────────────────────────

def recomendar(
    tema: str,
    candidatos: list[dict],
    limite: int = 5,
    metodo: str = "textual",
    alpha: float = 0.4,
    modelo_embeddings=None,
    contexto: dict | None = None,
) -> dict:
    """Devuelve las recomendaciones para *tema* con el método indicado.

    Parámetros
    ----------
    tema : str
        Texto de búsqueda del usuario.
    candidatos : list[dict]
        Lista de registros del catálogo o resultados de YouTube.
    limite : int
        Máximo de resultados a devolver (1-5).
    metodo : str
        'textual' | 'semantico' | 'hibrido'
    alpha : float
        Peso del componente textual en modo 'hibrido' (0.0–1.0).
    modelo_embeddings : ModeloEmbeddings | None
        Instancia reutilizable del modelo.
    contexto : dict | None
        Contexto pedagógico opcional (nivel, disciplina, usuario_id).

    Devuelve
    --------
    dict con: metodo, datos, consulta, terminos_utilizados, resultados.
    """
    terminos = normalizar(tema)
    datos_origen = _datos_origen(candidatos)

    if not terminos and metodo == "textual":
        res = _respuesta_vacia(tema, terminos, metodo, datos_origen)
        if contexto:
            res["contexto"] = contexto
        return res

    # ── Modo textual (E1) ────────────────────────────────────────────
    if metodo == "textual":
        res = _recomendar_textual(tema, candidatos, limite, terminos, datos_origen)
        if contexto:
            res["contexto"] = contexto
        return res

    # ── Modos semántico e híbrido (E3) ───────────────────────────────
    if modelo_embeddings is None:
        from .semantico import ModeloEmbeddings
        modelo_embeddings = ModeloEmbeddings()

    punts_sem = modelo_embeddings.puntuar(tema, candidatos)

    if metodo == "semantico":
        res = _recomendar_semantico(
            tema, candidatos, limite, terminos, punts_sem, datos_origen,
            modelo_embeddings.nombre_modelo,
        )
    elif metodo == "hibrido":
        res = _recomendar_hibrido(
            tema, candidatos, limite, terminos, punts_sem, datos_origen,
            alpha, modelo_embeddings.nombre_modelo,
        )
    else:
        res = _recomendar_textual(tema, candidatos, limite, terminos, datos_origen)

    if contexto:
        res["contexto"] = contexto
    return res


# ── Implementaciones por modo ──────────────────────────────────────

def _respuesta_vacia(tema, terminos, metodo, datos_origen):
    return {
        "metodo": metodo,
        "datos": datos_origen,
        "consulta": tema,
        "terminos_utilizados": terminos,
        "mensaje": "La consulta no contiene términos utilizables después de normalizar.",
        "resultados": [],
    }


def _recomendar_textual(tema, candidatos, limite, terminos, datos_origen):
    evaluados = []
    for cand in candidatos:
        punt, coincidencias = puntuar(terminos, cand)
        if punt > 0:
            item = _item_base(cand)
            item["puntuacion"] = round(punt, 4)
            item["coincidencias"] = coincidencias
            evaluados.append(item)

    evaluados.sort(key=lambda r: (-r["puntuacion"], r["id"]))

    return {
        "metodo": "coincidencia_textual",
        "datos": datos_origen,
        "consulta": tema,
        "terminos_utilizados": terminos,
        "resultados": evaluados[:limite],
    }


def _recomendar_semantico(
    tema, candidatos, limite, terminos, punts_sem, datos_origen, nombre_modelo
):
    evaluados = []
    for cand, punt_sem in zip(candidatos, punts_sem):
        if punt_sem >= UMBRAL_SEMANTICO:
            item = _item_base(cand)
            item["puntuacion"] = round(punt_sem, 4)
            item["similitud_semantica"] = round(punt_sem, 4)
            _, coincidencias = puntuar(terminos, cand)
            item["coincidencias"] = coincidencias
            evaluados.append(item)

    evaluados.sort(key=lambda r: (-r["puntuacion"], r["id"]))

    return {
        "metodo": f"semantico ({nombre_modelo})",
        "datos": datos_origen,
        "consulta": tema,
        "terminos_utilizados": terminos,
        "resultados": evaluados[:limite],
    }


def _recomendar_hibrido(
    tema, candidatos, limite, terminos, punts_sem, datos_origen, alpha, nombre_modelo
):
    evaluados = []
    for cand, punt_sem in zip(candidatos, punts_sem):
        punt_txt, coincidencias = puntuar(terminos, cand)
        punt_combinada = alpha * punt_txt + (1.0 - alpha) * punt_sem

        if punt_txt > 0 or punt_sem >= UMBRAL_SEMANTICO:
            item = _item_base(cand)
            item["puntuacion"] = round(punt_combinada, 4)
            item["puntuacion_textual"] = round(punt_txt, 4)
            item["similitud_semantica"] = round(punt_sem, 4)
            item["coincidencias"] = coincidencias
            evaluados.append(item)

    evaluados.sort(key=lambda r: (-r["puntuacion"], r["id"]))

    return {
        "metodo": f"hibrido (alpha={alpha}, modelo={nombre_modelo})",
        "datos": datos_origen,
        "consulta": tema,
        "terminos_utilizados": terminos,
        "alpha_textual": alpha,
        "resultados": evaluados[:limite],
    }

