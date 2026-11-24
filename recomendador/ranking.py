"""
ranking.py – Función de puntuación por coincidencia textual, semántica e híbrida.

Modos disponibles
-----------------
textual   – Proporción de términos de la consulta presentes en el candidato (E1).
semantico – Similitud de coseno con embeddings de sentence-transformers (E3).
hibrido   – Combinación ponderada de textual y semántico (alpha·textual + (1-alpha)·semantico).
hibrido_colaborativo – Filtro semántico seguido de contenido + vecinos de usuario (E5).

Conserva el contexto opcional de E4. El enriquecimiento de metadatos es futuro.
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
    matriz_utilidad: dict | None = None,
    peso_semantico: float = 0.7,
    umbral_semantico: float = UMBRAL_SEMANTICO,
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
        'textual' | 'semantico' | 'hibrido' (legado) | 'hibrido_colaborativo'
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

    if metodo == "hibrido_colaborativo":
        if not 0 <= peso_semantico <= 1 or not 0 <= umbral_semantico <= 1:
            raise ValueError("El peso y el umbral semántico deben estar entre 0 y 1.")
        if not tema.strip():
            return _respuesta_vacia(tema, terminos, metodo, datos_origen)
        if not 1 <= limite <= 5:
            raise ValueError("El límite debe estar entre 1 y 5.")

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
    elif metodo == "hibrido_colaborativo":
        res = _recomendar_colaborativo(
            tema, candidatos, limite, terminos, punts_sem, datos_origen,
            modelo_embeddings.nombre_modelo, contexto or {},
            matriz_utilidad or {}, peso_semantico, umbral_semantico,
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


def _recomendar_colaborativo(tema, candidatos, limite, terminos, puntuaciones,
                           origen, modelo, contexto, matriz, peso, umbral):
    """Evalúa TODOS los candidatos antes de limitar el ranking final a cinco."""
    from .colaborativo import predecir_colaborativo
    import math

    if len(candidatos) != len(puntuaciones):
        raise ValueError("Falta una puntuación semántica por candidato.")
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in puntuaciones):
        raise ValueError("Las puntuaciones semánticas deben ser finitas entre 0 y 1.")
    filtrados = [(c, p) for c, p in zip(candidatos, puntuaciones) if p >= umbral]
    predicciones = predecir_colaborativo(
        contexto.get("usuario_id"), [c["id"] for c, _ in filtrados], matriz,
    )
    resultados = []
    for candidato, semantica in filtrados:
        item = _item_base(candidato)
        prediccion = predicciones[candidato["id"]]
        colaborativa = prediccion["puntuacion_colaborativa"]
        efectiva = 1.0 if colaborativa is None else peso
        puntuacion = semantica if colaborativa is None else (
            efectiva * semantica + (1 - efectiva) * colaborativa)
        item.update(prediccion)
        item.update({
            "similitud_semantica": round(semantica, 6),
            "puntuacion_colaborativa": None if colaborativa is None else round(colaborativa, 6),
            "puntuacion": round(puntuacion, 6),
            "peso_semantico_efectivo": efectiva,
            "estrategia": "respaldo_semantico" if colaborativa is None else "semantico_colaborativo",
            "coincidencias": puntuar(terminos, candidato)[1],
        })
        resultados.append(item)
    resultados.sort(key=lambda r: (-r["puntuacion"], r["id"]))
    return {
        "metodo": "hibrido_colaborativo", "modelo": modelo, "datos": origen,
        "consulta": tema, "terminos_utilizados": terminos,
        "peso_semantico": peso, "umbral_semantico": umbral,
        "texto_analizado": ["titulo", "descripcion"],
        "enriquecimiento": "pendiente",
        "filtrado": {"candidatos": len(candidatos), "aceptados": len(filtrados),
                     "descartados": len(candidatos) - len(filtrados)},
        "resultados": resultados[:limite],
    }


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

