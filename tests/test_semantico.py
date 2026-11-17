"""
test_semantico.py – Pruebas unitarias para el módulo de análisis semántico (E3).

Todas las pruebas simulan el modelo de sentence-transformers con mocks,
por lo que no requieren descarga del modelo ni numpy instalado.
"""

import math
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers de fixtures
# ---------------------------------------------------------------------------

CANDIDATOS_DEMO = [
    {
        "id": "v001",
        "titulo": "Bases de datos relacionales",
        "descripcion": "Introducción a SQL y modelos relacionales.",
        "origen": "simulado",
    },
    {
        "id": "v002",
        "titulo": "Machine Learning con Python",
        "descripcion": "Regresión, clasificación y clustering.",
        "origen": "simulado",
    },
    {
        "id": "v003",
        "titulo": "Redes de computadoras",
        "descripcion": "Protocolos TCP/IP y modelo OSI.",
        "origen": "simulado",
    },
]


class _FakeEmbeddings:
    """Reemplaza numpy arrays para pruebas sin numpy.

    Soporta indexación por entero [i] y len().
    Cada fila es una lista de floats; la primera fila es la consulta,
    el resto son los candidatos.
    """

    def __init__(self, filas: list[list[float]]) -> None:
        self._filas = filas

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return _FakeVector(self._filas[idx])
        # slice → devuelve otra _FakeEmbeddings (no se usa en semantico.py v2)
        return _FakeEmbeddings(self._filas[idx])

    def __len__(self):
        return len(self._filas)


class _FakeVector:
    """Vector 1-D que soporta indexación y len()."""

    def __init__(self, datos: list[float]) -> None:
        self._datos = datos

    def __getitem__(self, idx):
        return self._datos[idx]

    def __len__(self):
        return len(self._datos)


class _FakeSlice:
    """No se usa en la versión actual de semantico.py (loop puro)."""
    pass


class _FakeResult:
    def __init__(self, valores: list[float]) -> None:
        self._valores = valores

    def tolist(self) -> list[float]:
        return list(self._valores)


def _embeddings_desde_similitudes(similitudes: list[float]) -> _FakeEmbeddings:
    """Construye embeddings 2-D coherentes con las similitudes pedidas.

    Estrategia geométrica:
      consulta = [1, 0, 0]
      candidato_i = [sim_i, sqrt(1 - sim_i²), 0]
      → cos(consulta, candidato_i) = sim_i
    """
    dim = 3
    filas: list[list[float]] = [[1.0] + [0.0] * (dim - 1)]
    for s in similitudes:
        s = max(0.0, min(1.0, s))
        orto = math.sqrt(max(0.0, 1.0 - s * s))
        filas.append([s, orto] + [0.0] * (dim - 2))
    return _FakeEmbeddings(filas)


def _mock_sentence_transformers(similitudes: list[float]):
    """Devuelve un módulo sentence_transformers simulado."""
    embeddings = _embeddings_desde_similitudes(similitudes)

    modelo_st = MagicMock()
    modelo_st.encode.return_value = embeddings

    st_module = MagicMock()
    st_module.SentenceTransformer.return_value = modelo_st
    return st_module, modelo_st


# ---------------------------------------------------------------------------
# Pruebas de ModeloEmbeddings
# ---------------------------------------------------------------------------

class TestModeloEmbeddings(unittest.TestCase):
    """Pruebas de la clase ModeloEmbeddings."""

    def _nueva_instancia(self, nombre="modelo-prueba"):
        import importlib
        import recomendador.semantico as sem
        importlib.reload(sem)
        return sem.ModeloEmbeddings(nombre_modelo=nombre)

    # ── Construcción ─────────────────────────────────────────────────

    def test_nombre_modelo_por_defecto(self):
        """El nombre por defecto es MODELO_DEFECTO."""
        import recomendador.semantico as sem
        m = sem.ModeloEmbeddings()
        self.assertEqual(m.nombre_modelo, sem.MODELO_DEFECTO)

    def test_nombre_modelo_personalizado(self):
        """El constructor acepta un nombre de modelo personalizado."""
        m = self._nueva_instancia("mi-modelo")
        self.assertEqual(m.nombre_modelo, "mi-modelo")

    def test_no_cargado_al_crear(self):
        """El modelo NO se carga en memoria al instanciar."""
        m = self._nueva_instancia()
        self.assertFalse(m.cargado)

    def test_nombre_modelo_via_env(self):
        """La variable RECOMENDADOR_MODELO_EMBEDDINGS se respeta."""
        import recomendador.semantico as sem
        with patch.dict("os.environ", {sem.ENV_MODELO: "modelo-env"}):
            import importlib
            importlib.reload(sem)
            m = sem.ModeloEmbeddings()
            self.assertEqual(m.nombre_modelo, "modelo-env")

    # ── puntuar() – lista vacía ───────────────────────────────────────

    def test_puntuar_sin_candidatos_devuelve_lista_vacia(self):
        """puntuar() con candidatos vacíos devuelve []."""
        m = self._nueva_instancia()
        self.assertEqual(m.puntuar("bases de datos", []), [])

    # ── puntuar() – comportamiento con mock ──────────────────────────

    def _puntuar_mock(self, similitudes, consulta="bases de datos"):
        st_mod, _ = _mock_sentence_transformers(similitudes)
        with patch.dict("sys.modules", {"sentence_transformers": st_mod}):
            import importlib
            import recomendador.semantico as sem
            importlib.reload(sem)
            m = sem.ModeloEmbeddings()
            return m.puntuar(consulta, CANDIDATOS_DEMO[:len(similitudes)])

    def test_longitud_igual_a_candidatos(self):
        """puntuar() devuelve exactamente tantos valores como candidatos."""
        resultado = self._puntuar_mock([0.9, 0.3, 0.1])
        self.assertEqual(len(resultado), 3)

    def test_valores_en_rango_01(self):
        """puntuar() devuelve valores en [0.0, 1.0]."""
        resultado = self._puntuar_mock([0.85, 0.20, 0.10])
        for p in resultado:
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)

    def test_no_produce_valores_negativos(self):
        """puntuar() recorta a 0.0 si el coseno es negativo."""
        # Forzamos un vector con coseno negativo
        emb_negativo = _FakeEmbeddings([
            [1.0, 0.0, 0.0],   # consulta
            [-0.5, 0.86, 0.0], # candidato con coseno < 0
        ])
        st_mod = MagicMock()
        st_mod.SentenceTransformer.return_value.encode.return_value = emb_negativo
        with patch.dict("sys.modules", {"sentence_transformers": st_mod}):
            import importlib
            import recomendador.semantico as sem
            importlib.reload(sem)
            m = sem.ModeloEmbeddings()
            resultado = m.puntuar("tema", CANDIDATOS_DEMO[:1])
        self.assertGreaterEqual(resultado[0], 0.0)

    def test_encode_llamado_con_normalize_true(self):
        """El encode se llama con normalize_embeddings=True."""
        st_mod, mock_st = _mock_sentence_transformers([0.5])
        with patch.dict("sys.modules", {"sentence_transformers": st_mod}):
            import importlib
            import recomendador.semantico as sem
            importlib.reload(sem)
            m = sem.ModeloEmbeddings()
            m.puntuar("sql", CANDIDATOS_DEMO[:1])
        _, kwargs = mock_st.encode.call_args
        self.assertTrue(kwargs.get("normalize_embeddings", False))

    # ── Error de importación ─────────────────────────────────────────

    def test_importerror_sin_sentence_transformers(self):
        """Si sentence_transformers no está, puntuar() lanza ImportError."""
        with patch.dict("sys.modules", {"sentence_transformers": None}):
            import importlib
            import recomendador.semantico as sem
            importlib.reload(sem)
            m = sem.ModeloEmbeddings()
            with self.assertRaises(ImportError) as ctx:
                m.puntuar("bases de datos", CANDIDATOS_DEMO)
        self.assertIn("pip install", str(ctx.exception))

    # ── Texto del candidato ──────────────────────────────────────────

    def test_texto_candidato_titulo_y_descripcion(self):
        """_texto_candidato combina título y descripción."""
        import recomendador.semantico as sem
        texto = sem.ModeloEmbeddings._texto_candidato({
            "titulo": "SQL avanzado",
            "descripcion": "Consultas complejas",
        })
        self.assertIn("SQL avanzado", texto)
        self.assertIn("Consultas complejas", texto)

    def test_texto_candidato_sin_descripcion(self):
        """_texto_candidato funciona sin descripción."""
        import recomendador.semantico as sem
        texto = sem.ModeloEmbeddings._texto_candidato({"titulo": "Solo título"})
        self.assertIn("Solo título", texto)

    def test_texto_candidato_vacio_usa_fallback(self):
        """_texto_candidato devuelve texto de respaldo para dict vacío."""
        import recomendador.semantico as sem
        texto = sem.ModeloEmbeddings._texto_candidato({})
        self.assertEqual(texto, "sin descripción")


# ---------------------------------------------------------------------------
# Pruebas de integración: ranking.recomendar con modo semántico e híbrido
# ---------------------------------------------------------------------------

class TestRecomendarSemantico(unittest.TestCase):
    """Integración entre ranking.recomendar y ModeloEmbeddings."""

    def _mock_modelo(self, punts: list[float]):
        mock = MagicMock()
        mock.puntuar.return_value = punts
        mock.nombre_modelo = "modelo-mock"
        return mock

    def test_modo_semantico_devuelve_metodo_correcto(self):
        """El campo 'metodo' en modo semántico contiene 'semantico'."""
        from recomendador.ranking import recomendar
        modelo = self._mock_modelo([0.9, 0.3, 0.1])
        res = recomendar("bases de datos", CANDIDATOS_DEMO, metodo="semantico", modelo_embeddings=modelo)
        self.assertIn("semantico", res["metodo"])

    def test_modo_semantico_filtra_por_umbral(self):
        """Candidatos bajo el umbral no aparecen en modo semántico."""
        from recomendador.ranking import recomendar, UMBRAL_SEMANTICO
        punts = [0.9, 0.05, 0.03]
        modelo = self._mock_modelo(punts)
        res = recomendar("bases de datos", CANDIDATOS_DEMO, metodo="semantico", modelo_embeddings=modelo)
        self.assertEqual(len(res["resultados"]), 1)
        self.assertEqual(res["resultados"][0]["id"], "v001")

    def test_modo_semantico_ordena_descendente(self):
        """Los resultados semánticos están ordenados de mayor a menor."""
        from recomendador.ranking import recomendar
        punts = [0.5, 0.9, 0.7]
        modelo = self._mock_modelo(punts)
        res = recomendar("redes", CANDIDATOS_DEMO, metodo="semantico", modelo_embeddings=modelo)
        ps = [r["puntuacion"] for r in res["resultados"]]
        self.assertEqual(ps, sorted(ps, reverse=True))

    def test_modo_semantico_incluye_similitud_semantica(self):
        """Cada resultado semántico incluye el campo 'similitud_semantica'."""
        from recomendador.ranking import recomendar
        modelo = self._mock_modelo([0.8, 0.5, 0.2])
        res = recomendar("sql", CANDIDATOS_DEMO, metodo="semantico", modelo_embeddings=modelo)
        for r in res["resultados"]:
            self.assertIn("similitud_semantica", r)

    def test_modo_hibrido_combina_puntuaciones(self):
        """En modo híbrido cada resultado incluye puntuacion_textual y similitud_semantica."""
        from recomendador.ranking import recomendar
        modelo = self._mock_modelo([0.6, 0.2, 0.1])
        res = recomendar(
            "datos relacionales", CANDIDATOS_DEMO,
            metodo="hibrido", alpha=0.4, modelo_embeddings=modelo,
        )
        self.assertIn("hibrido", res["metodo"])
        for r in res["resultados"]:
            self.assertIn("puntuacion_textual", r)
            self.assertIn("similitud_semantica", r)

    def test_modo_hibrido_incluye_alpha_en_respuesta(self):
        """La respuesta híbrida incluye el valor de alpha utilizado."""
        from recomendador.ranking import recomendar
        modelo = self._mock_modelo([0.5, 0.4, 0.3])
        res = recomendar("sql", CANDIDATOS_DEMO, metodo="hibrido", alpha=0.3, modelo_embeddings=modelo)
        self.assertAlmostEqual(res["alpha_textual"], 0.3)

    def test_modo_textual_no_usa_modelo(self):
        """En modo textual, el modelo de embeddings nunca se invoca."""
        from recomendador.ranking import recomendar
        modelo = self._mock_modelo([])
        recomendar("datos", CANDIDATOS_DEMO, metodo="textual", modelo_embeddings=modelo)
        modelo.puntuar.assert_not_called()

    def test_modo_semantico_sin_resultados_sobre_umbral(self):
        """Si ningún candidato supera el umbral, resultados es lista vacía."""
        from recomendador.ranking import recomendar
        modelo = self._mock_modelo([0.01, 0.02, 0.03])
        res = recomendar("xyz123", CANDIDATOS_DEMO, metodo="semantico", modelo_embeddings=modelo)
        self.assertEqual(res["resultados"], [])

    def test_modo_hibrido_incluye_candidatos_solo_textuales(self):
        """En modo híbrido se incluyen candidatos con puntuación textual > 0 aunque semántica sea baja."""
        from recomendador.ranking import recomendar
        # "relacionales" debería encontrarse textualmente en v001
        modelo = self._mock_modelo([0.0, 0.0, 0.0])  # semántica inútil
        res = recomendar("relacionales", CANDIDATOS_DEMO, metodo="hibrido", modelo_embeddings=modelo)
        ids = [r["id"] for r in res["resultados"]]
        self.assertIn("v001", ids)


if __name__ == "__main__":
    unittest.main()
