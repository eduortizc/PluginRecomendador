"""
test_ranking.py – Pruebas del motor de recomendación E1.

Ejecutar desde la raíz del proyecto:
    python3 -m unittest tests.test_ranking -v
"""

import json
import tempfile
import unittest
from pathlib import Path

from recomendador.catalogo import cargar_catalogo, ErrorCatalogo, ruta_catalogo_default
from recomendador.ranking import normalizar, puntuar, recomendar


# ── Pruebas de normalización ───────────────────────────────────────

class TestNormalizar(unittest.TestCase):

    def test_minusculas(self):
        self.assertEqual(normalizar("Bases De Datos"), ["bases", "datos"])

    def test_acentos(self):
        self.assertEqual(normalizar("programación"), ["programacion"])

    def test_palabras_excluidas(self):
        resultado = normalizar("el diseño de la base")
        self.assertNotIn("el", resultado)
        self.assertNotIn("de", resultado)
        self.assertNotIn("la", resultado)
        self.assertIn("diseno", resultado)
        self.assertIn("base", resultado)

    def test_solo_palabras_excluidas(self):
        self.assertEqual(normalizar("de la en el"), [])

    def test_cadena_vacia(self):
        self.assertEqual(normalizar(""), [])

    def test_caracteres_especiales(self):
        resultado = normalizar("TCP/IP y redes")
        self.assertIn("tcp", resultado)
        self.assertIn("ip", resultado)
        self.assertIn("redes", resultado)


# ── Pruebas de puntuación ──────────────────────────────────────────

class TestPuntuar(unittest.TestCase):

    def setUp(self):
        self.candidato = {
            "id": "demo_001",
            "titulo": "Introducción a las bases de datos relacionales",
            "descripcion": "Conceptos fundamentales de bases de datos.",
            "origen": "simulado",
            "url": None,
        }

    def test_coincidencia_total(self):
        terms = normalizar("bases datos")
        punt, coinc = puntuar(terms, self.candidato)
        self.assertEqual(punt, 1.0)
        self.assertIn("bases", coinc)
        self.assertIn("datos", coinc)

    def test_coincidencia_parcial(self):
        terms = normalizar("bases redes")
        punt, coinc = puntuar(terms, self.candidato)
        self.assertAlmostEqual(punt, 0.5)
        self.assertIn("bases", coinc)
        self.assertNotIn("redes", coinc)

    def test_sin_coincidencia(self):
        terms = normalizar("redes computadoras")
        punt, coinc = puntuar(terms, self.candidato)
        self.assertEqual(punt, 0.0)
        self.assertEqual(coinc, [])

    def test_consulta_vacia(self):
        punt, coinc = puntuar([], self.candidato)
        self.assertEqual(punt, 0.0)
        self.assertEqual(coinc, [])


# ── Pruebas del recomendador ───────────────────────────────────────

class TestRecomendar(unittest.TestCase):

    def setUp(self):
        self.catalogo = cargar_catalogo()

    def test_consulta_con_resultados(self):
        r = recomendar("bases de datos", self.catalogo)
        self.assertEqual(r["metodo"], "coincidencia_textual")
        self.assertEqual(r["datos"], "simulados")
        self.assertGreater(len(r["resultados"]), 0)
        # Deben incluir los registros sobre bases de datos.
        ids = [res["id"] for res in r["resultados"]]
        self.assertIn("demo_001", ids)
        self.assertIn("demo_002", ids)

    def test_orden_descendente(self):
        r = recomendar("bases de datos", self.catalogo)
        puntuaciones = [res["puntuacion"] for res in r["resultados"]]
        self.assertEqual(puntuaciones, sorted(puntuaciones, reverse=True))

    def test_mayusculas_y_acentos(self):
        r1 = recomendar("BASES DE DATOS", self.catalogo)
        r2 = recomendar("bases de datos", self.catalogo)
        r3 = recomendar("Programación", self.catalogo)
        r4 = recomendar("programacion", self.catalogo)
        self.assertEqual(r1["resultados"], r2["resultados"])
        self.assertEqual(
            [x["id"] for x in r3["resultados"]],
            [x["id"] for x in r4["resultados"]],
        )

    def test_sin_coincidencias(self):
        r = recomendar("gastronomía molecular", self.catalogo)
        self.assertEqual(r["resultados"], [])

    def test_consulta_solo_stopwords(self):
        r = recomendar("de la en el", self.catalogo)
        self.assertEqual(r["resultados"], [])
        self.assertIn("mensaje", r)

    def test_consulta_vacia(self):
        r = recomendar("", self.catalogo)
        self.assertEqual(r["resultados"], [])
        self.assertIn("mensaje", r)

    def test_empate_por_id(self):
        """Cuando dos candidatos empatan, se ordena por id."""
        r = recomendar("bases de datos SQL", self.catalogo)
        resultados = r["resultados"]
        for i in range(len(resultados) - 1):
            if resultados[i]["puntuacion"] == resultados[i + 1]["puntuacion"]:
                self.assertLessEqual(resultados[i]["id"], resultados[i + 1]["id"])

    def test_limite(self):
        r = recomendar("datos", self.catalogo, limite=2)
        self.assertLessEqual(len(r["resultados"]), 2)

    def test_no_rellena_resultados(self):
        """No inventa resultados para llegar al límite."""
        r = recomendar("gastronomía", self.catalogo, limite=5)
        self.assertEqual(len(r["resultados"]), 0)


# ── Pruebas de catálogo ────────────────────────────────────────────

class TestCatalogo(unittest.TestCase):

    def test_carga_default(self):
        videos = cargar_catalogo()
        self.assertGreaterEqual(len(videos), 8)

    def test_ruta_inexistente(self):
        with self.assertRaises(ErrorCatalogo):
            cargar_catalogo(Path("/tmp/no_existe.json"))

    def test_json_invalido(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{esto no es json")
            f.flush()
            with self.assertRaises(ErrorCatalogo):
                cargar_catalogo(Path(f.name))

    def test_registro_incompleto(self):
        datos = {"videos": [{"id": "x"}]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(datos, f)
            f.flush()
            with self.assertRaises(ErrorCatalogo):
                cargar_catalogo(Path(f.name))


if __name__ == "__main__":
    unittest.main()
