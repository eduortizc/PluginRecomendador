"""Pruebas de E5 con valoraciones ficticias y puntuaciones semánticas controladas.

Comprueban software; no miden relevancia pedagógica ni eficacia con usuarios.
"""
import json
import io
from contextlib import redirect_stdout, redirect_stderr
import tempfile
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import urlencode
from urllib.request import urlopen

from recomendador.colaborativo import predecir_colaborativo
from recomendador.interacciones import GestorInteracciones
from recomendador.ranking import recomendar


MATRIZ = {
    "objetivo": {"comun1": 5, "comun2": 1},
    "vecino": {"comun1": 5, "comun2": 1, "a": 1, "b": 5, "c": 5},
    "otro": {"ajeno": 5, "a": 5},
}
CANDIDATOS = [{"id": v, "titulo": "Video ficticio " + v, "origen": "simulado"}
              for v in "abcd"]


def modelo(scores):
    return Mock(nombre_modelo="embeddings_controlados_prueba",
                puntuar=Mock(return_value=scores))


class TestColaborativo(unittest.TestCase):
    def recomendar(self, **kwargs):
        config = dict(metodo="hibrido_colaborativo", modelo_embeddings=modelo([.8, .7, .1, .5]),
                      contexto={"usuario_id": "objetivo"}, matriz_utilidad=MATRIZ)
        config.update(kwargs)
        return recomendar("tema", CANDIDATOS, **config)

    def test_puntuaciones_y_cero_real(self):
        p = predecir_colaborativo("objetivo", ["a", "b", "d"], MATRIZ)
        self.assertEqual(p["a"]["puntuacion_colaborativa"], 0)
        self.assertEqual(p["b"]["puntuacion_colaborativa"], 1)
        self.assertEqual(p["a"]["vecinos_utilizados"], 1)
        self.assertIsNone(p["d"]["puntuacion_colaborativa"])

    def test_promedio_ponderado_por_similitud(self):
        matriz = {**MATRIZ, "vecino2": {"comun1": 1, "comun2": 5, "b": 1}}
        p = predecir_colaborativo("objetivo", ["b"], matriz)["b"]
        # cos(5,1; 1,5)=5/13. Predicción normalizada: 1/(1+5/13).
        self.assertAlmostEqual(p["puntuacion_colaborativa"], 13 / 18)
        self.assertEqual(p["vecinos_utilizados"], 2)

    def test_una_coincidencia_no_basta(self):
        matriz = {"u": {"x": 4}, "v": {"x": 4, "a": 5}}
        p = predecir_colaborativo("u", ["a"], matriz)["a"]
        self.assertEqual(p["motivo_respaldo"], "sin_vecinos_suficientes")

    def test_usuario_nuevo_y_anonimo(self):
        for usuario, motivo in [("nuevo", "usuario_sin_valoraciones"), (None, "sin_usuario")]:
            with self.subTest(usuario=usuario):
                p = predecir_colaborativo(usuario, ["a"], MATRIZ)["a"]
                self.assertIsNone(p["puntuacion_colaborativa"])
                self.assertEqual(p["motivo_respaldo"], motivo)

    def test_reordena_antes_de_cortar_y_filtra_semantica(self):
        r = self.recomendar(limite=1)
        self.assertEqual(r["resultados"][0]["id"], "b")
        self.assertAlmostEqual(r["resultados"][0]["puntuacion"], .79)
        self.assertEqual(r["filtrado"], {"candidatos": 4, "aceptados": 3, "descartados": 1})
        # c recibe 5 estrellas del vecino pero no supera el filtro semántico.
        self.assertNotIn("c", [v["id"] for v in self.recomendar()["resultados"]])

    def test_recurso_nuevo_conserva_score_semantico(self):
        nuevo = next(v for v in self.recomendar()["resultados"] if v["id"] == "d")
        self.assertEqual(nuevo["puntuacion"], .5)
        self.assertEqual(nuevo["peso_semantico_efectivo"], 1)
        self.assertEqual(nuevo["motivo_respaldo"], "video_sin_valoraciones_de_vecinos")

    def test_sin_historial_equivale_a_semantico(self):
        m = modelo([.8, .7, .1, .5])
        sem = recomendar("tema", CANDIDATOS, metodo="semantico", modelo_embeddings=m)
        hibrido = self.recomendar(matriz_utilidad={})
        self.assertEqual([(r["id"], r["puntuacion"]) for r in sem["resultados"]],
                         [(r["id"], r["puntuacion"]) for r in hibrido["resultados"]])

    def test_empate_determinista_sin_mutar_candidatos(self):
        antes = json.dumps(CANDIDATOS)
        r = self.recomendar(matriz_utilidad={}, modelo_embeddings=modelo([.5] * 4))
        self.assertEqual([v["id"] for v in r["resultados"]], list("abcd"))
        self.assertEqual(json.dumps(CANDIDATOS), antes)

    def test_validaciones_y_alineacion(self):
        for config in [{"peso_semantico": float("nan")}, {"peso_semantico": 2},
                       {"umbral_semantico": -1}, {"modelo_embeddings": modelo([.5])},
                       {"modelo_embeddings": modelo([float("inf")] * 4)}]:
            with self.subTest(config=config), self.assertRaises(ValueError):
                self.recomendar(**config)
        with self.assertRaises(ValueError):
            predecir_colaborativo("u", ["a"], {"u": {"a": float("nan")}})

    def test_vacio_y_todos_descartados(self):
        self.assertEqual(self.recomendar(modelo_embeddings=modelo([0] * 4))["resultados"], [])
        r = recomendar("tema", [], metodo="hibrido_colaborativo", modelo_embeddings=modelo([]))
        self.assertEqual(r["resultados"], [])

    def test_impresiones_no_crean_preferencias(self):
        with tempfile.TemporaryDirectory() as tmp:
            gestor = GestorInteracciones(Path(tmp) / "eventos.json")
            gestor.registrar_evento("u", "a", "impresion")
            gestor.registrar_evento("u", "b", "apertura")
            self.assertEqual(gestor.generar_matriz_utilidad(solo_valoraciones=True), {})
            gestor.registrar_evento("u", "a", "valoracion", 5)
            gestor.guardar()
            recargado = GestorInteracciones(gestor.ruta)
            self.assertEqual(recargado.generar_matriz_utilidad(solo_valoraciones=True), {"u": {"a": 5}})


class TestBuscadorHibrido(unittest.TestCase):
    def test_consola_usa_historial_y_guarda_impresiones_sin_alterar_matriz(self):
        from recomendador.__main__ import main
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "valoraciones.json"
            gestor = GestorInteracciones(ruta)
            for usuario, vals in MATRIZ.items():
                for video, valor in vals.items():
                    gestor.registrar_evento(usuario, video, "valoracion", valor)
            gestor.guardar()
            stdout = io.StringIO()
            argv = ["recomendador", "--tema", "tema", "--metodo", "hibrido_colaborativo",
                    "--usuario", "objetivo", "--interacciones", str(ruta), "--limite", "1"]
            with patch("sys.argv", argv), \
                 patch("recomendador.__main__.cargar_catalogo", return_value=CANDIDATOS), \
                 patch("recomendador.semantico.ModeloEmbeddings", return_value=modelo([.8, .7, .1, .5])), \
                 redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                main()
            self.assertEqual(json.loads(stdout.getvalue())["resultados"][0]["id"], "b")
            recargado = GestorInteracciones(ruta)
            self.assertEqual(recargado.eventos[-1]["tipo"], "impresion")
            self.assertEqual(recargado.generar_matriz_utilidad(solo_valoraciones=True), MATRIZ)

    def test_http_valoracion_persistente_y_ranking_entre_usuarios(self):
        import recomendador.servidor as web
        with tempfile.TemporaryDirectory() as tmp:
            gestores = {f: GestorInteracciones(Path(tmp) / (f + ".json"))
                        for f in ("youtube", "simulado")}
            with patch.object(web, "_gestores_interacciones", gestores), \
                 patch.object(web, "_obtener_modelo", return_value=modelo([.8, .7, .1, .5])), \
                 patch.object(web, "cargar_catalogo", return_value=CANDIDATOS):
                servidor = HTTPServer(("127.0.0.1", 0), web._ManejadorRecomendador)
                hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
                hilo.start()

                def get(ruta, **params):
                    with urlopen(f"http://127.0.0.1:{servidor.server_port}{ruta}?{urlencode(params)}", timeout=5) as resp:
                        return json.load(resp)

                try:
                    for usuario, vals in MATRIZ.items():
                        for video, valor in vals.items():
                            get("/api/interaccion", fuente="simulado", usuario_id=usuario,
                                video_id=video, tipo="valoracion", valor=valor)
                    r = get("/api/recomendar", fuente="simulado", metodo="hibrido_colaborativo",
                            usuario_id="objetivo", tema="tema", limite=1)
                    self.assertEqual(r["resultados"][0]["id"], "b")
                    self.assertEqual(r["resultados"][0]["estrategia"], "semantico_colaborativo")
                    self.assertEqual(gestores["youtube"].eventos, [])
                    recargado = GestorInteracciones(gestores["simulado"].ruta)
                    self.assertEqual(recargado.generar_matriz_utilidad(solo_valoraciones=True), MATRIZ)
                finally:
                    servidor.shutdown()
                    hilo.join(timeout=5)
                    servidor.server_close()
