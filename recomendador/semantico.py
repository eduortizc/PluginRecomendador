"""
semantico.py – Análisis semántico con sentence-transformers (E3).

Genera embeddings densos para la consulta y los candidatos usando un
modelo multilingüe preentrenado y calcula la similitud de coseno.

Modelo por defecto: paraphrase-multilingual-MiniLM-L12-v2
  - Multilingüe (50+ idiomas, incluye español e inglés).
  - Pesos FP32 de aproximadamente 471 MB; RAM y dependencias se contabilizan aparte.
  - Primera ejecución descarga el modelo desde HuggingFace; la duración depende de la red.

Cambiar el modelo
-----------------
Exporta la variable de entorno antes de ejecutar::

    export RECOMENDADOR_MODELO_EMBEDDINGS=all-MiniLM-L6-v2

O pásalo al constructor::

    modelo = ModeloEmbeddings("paraphrase-multilingual-mpnet-base-v2")

Uso típico
----------
    from recomendador.semantico import ModeloEmbeddings

    modelo = ModeloEmbeddings()
    puntuaciones = modelo.puntuar("bases de datos relacionales", candidatos)
    # → [0.82, 0.14, 0.61, ...]  (una por candidato, en el mismo orden)
"""

import os


# ── Nombre del modelo ────────────────────────────────────────────────────────
# Multilingüe ligero: buena cobertura de español e inglés sin GPU.
MODELO_DEFECTO = "paraphrase-multilingual-MiniLM-L12-v2"
ENV_MODELO = "RECOMENDADOR_MODELO_EMBEDDINGS"


def _nombre_modelo() -> str:
    """Devuelve el nombre del modelo activo (variable de entorno o defecto)."""
    return os.environ.get(ENV_MODELO, MODELO_DEFECTO)


# ── Clase principal ──────────────────────────────────────────────────────────

class ModeloEmbeddings:
    """Encapsula un SentenceTransformer para calcular similitud semántica.

    El modelo se carga de forma diferida (lazy) la primera vez que se
    llama a ``puntuar()``, para no ralentizar arranques sin búsqueda semántica.

    Parámetros
    ----------
    nombre_modelo : str | None
        Nombre o ruta del modelo HuggingFace. Si es ``None`` se usa
        ``RECOMENDADOR_MODELO_EMBEDDINGS`` o el valor de ``MODELO_DEFECTO``.

    Ejemplo
    -------
        modelo = ModeloEmbeddings()
        puntuaciones = modelo.puntuar("machine learning", candidatos)
        # candidatos con alta similitud → puntuación cercana a 1.0
    """

    def __init__(self, nombre_modelo: str | None = None) -> None:
        self._nombre: str = nombre_modelo or _nombre_modelo()
        self._modelo = None  # carga diferida

    # ── API pública ──────────────────────────────────────────────────────

    def puntuar(self, consulta: str, candidatos: list[dict]) -> list[float]:
        """Similitud de coseno entre la consulta y cada candidato.

        Parámetros
        ----------
        consulta : str
            Texto de búsqueda (tema del docente o estudiante).
        candidatos : list[dict]
            Registros con al menos 'titulo' y opcionalmente 'descripcion'.

        Devuelve
        --------
        list[float]
            Valores en [0.0, 1.0], mismo orden que ``candidatos``.
            Lista vacía si no hay candidatos.

        Lanza
        -----
        ImportError
            Si sentence-transformers no está instalado.
        """
        if not candidatos:
            return []

        modelo = self._cargar()
        textos = [self._texto_candidato(c) for c in candidatos]

        # Codificar consulta y candidatos en un solo batch (más eficiente)
        embeddings = modelo.encode(
            [consulta] + textos,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,  # norma L2 → coseno = producto punto
        )

        vec_consulta = embeddings[0]

        # Producto punto fila a fila (compatible con numpy arrays y mocks en tests)
        puntuaciones = [
            float(sum(embeddings[i + 1][j] * vec_consulta[j] for j in range(len(vec_consulta))))
            for i in range(len(candidatos))
        ]

        # Recortar a [0, 1]: coseno puede ser levemente negativo por precisión
        return [max(0.0, round(p, 6)) for p in puntuaciones]

    @property
    def nombre_modelo(self) -> str:
        """Nombre del modelo configurado."""
        return self._nombre

    @property
    def cargado(self) -> bool:
        """True si el modelo ya está en memoria."""
        return self._modelo is not None

    # ── Helpers privados ─────────────────────────────────────────────────

    def _cargar(self):
        """Carga el SentenceTransformer si aún no está en memoria."""
        if self._modelo is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise ImportError(
                    "sentence-transformers no está instalado.\n"
                    "Ejecuta en tu terminal:  pip install sentence-transformers"
                ) from exc
            self._modelo = SentenceTransformer(self._nombre)
        return self._modelo

    @staticmethod
    def _texto_candidato(candidato: dict) -> str:
        """Texto representativo de un candidato (título + descripción)."""
        partes = [
            candidato.get("titulo", ""),
            candidato.get("descripcion", ""),
        ]
        texto = " ".join(p for p in partes if p).strip()
        return texto if texto else "sin descripción"

