"""Contrato de integración. Las consultas externas y los embeddings se simulan."""
import argparse
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

import moodle_bridge as bridge
from recomendador.ranking import recomendar
from recomendador.youtube import ErrorYouTube


def argumentos(**cambios):
    valores = dict(tema="bases de datos", fuente="youtube", metodo="textual", limite=5,
                   max_candidatos=20, timeout=120, cache_dir="")
    valores.update(cambios)
    return argparse.Namespace(**valores)


class TestMoodleBridge(unittest.TestCase):
    def test_metadatos_llegan_al_resultado_incluyendo_cero(self):
        candidato = {"id": "prueba", "titulo": "Bases de datos", "descripcion": "SQL",
                     "origen": "youtube", "vistas": 0, "likes": 0,
                     "duracion": "PT0S", "duracion_segundos": 0}
        for metodo in ["textual", "semantico", "hibrido"]:
            modelo = Mock(nombre_modelo="mock")
            modelo.puntuar.return_value = [0.8]
            resultado = recomendar("bases de datos", [candidato], metodo=metodo, modelo_embeddings=modelo)
            for campo in ["descripcion", "vistas", "likes", "duracion", "duracion_segundos"]:
                self.assertEqual(resultado["resultados"][0][campo], candidato[campo])

    def test_youtube_utiliza_cliente_existente_y_parametros(self):
        candidato = {"id": "prueba", "titulo": "Bases de datos", "descripcion": "SQL", "origen": "youtube"}
        with patch("recomendador.youtube.buscar_videos_youtube", return_value=[candidato]) as buscar:
            datos, codigo = bridge.ejecutar(argumentos())
        self.assertEqual(codigo, 0)
        self.assertEqual(datos["datos"], "youtube")
        self.assertEqual(datos["texto_analizado"], ["titulo", "descripcion"])
        buscar.assert_called_once_with("bases de datos", max_resultados=20, timeout=15)

    def test_youtube_vacio_conserva_fuente_real(self):
        with patch("recomendador.youtube.buscar_videos_youtube", return_value=[]):
            datos, codigo = bridge.ejecutar(argumentos())
        self.assertEqual((codigo, datos["datos"], datos["resultados"]), (0, "youtube", []))

    def test_error_youtube_no_expone_clave(self):
        with patch("recomendador.youtube.buscar_videos_youtube", side_effect=ErrorYouTube(
                "https://example.invalid/?key=SECRETO", codigo="acceso_denegado")):
            datos, codigo = bridge.ejecutar(argumentos())
        self.assertEqual(codigo, 3)
        self.assertEqual(datos["error"]["codigo"], "acceso_denegado")
        self.assertNotIn("SECRETO", json.dumps(datos))

    def test_dependencia_ausente_no_genera_traceback_en_json(self):
        with patch("recomendador.youtube.buscar_videos_youtube", return_value=[]), patch(
                "recomendador.ranking.recomendar", side_effect=ImportError("ruta privada")):
            datos, codigo = bridge.ejecutar(argumentos(metodo="semantico"))
        self.assertEqual(codigo, 4)
        self.assertEqual(datos["error"]["codigo"], "dependencias")
        self.assertNotIn("ruta privada", json.dumps(datos))

    def test_modelo_falla_con_error_controlado(self):
        with patch("recomendador.youtube.buscar_videos_youtube", return_value=[]), patch(
                "recomendador.ranking.recomendar", side_effect=OSError("descarga fallida")):
            datos, codigo = bridge.ejecutar(argumentos(metodo="semantico"))
        self.assertEqual((codigo, datos["error"]["codigo"]), (6, "motor"))

    def test_consulta_vacia_y_extensa_se_rechazan(self):
        for consulta in ["   ", "x" * 501]:
            datos, codigo = bridge.ejecutar(argumentos(tema=consulta))
            self.assertEqual((codigo, datos["error"]["codigo"]), (2, "entrada_invalida"))

    def test_stdout_de_dependencia_se_separa(self):
        def cliente(*args, **kwargs):
            print("aviso con {llaves}")
            return []
        salida, avisos = StringIO(), StringIO()
        with patch("recomendador.youtube.buscar_videos_youtube", side_effect=cliente), redirect_stdout(salida), patch("sys.stderr", avisos):
            bridge.ejecutar(argumentos())
        self.assertEqual(salida.getvalue(), "")
        self.assertIn("aviso", avisos.getvalue())

    def test_timeout_del_subproceso_devuelve_json(self):
        salida = StringIO()
        with patch("moodle_bridge.subprocess.run", side_effect=subprocess.TimeoutExpired("worker", 5)), redirect_stdout(salida):
            codigo = bridge.main(["--tema", "SQL", "--timeout", "5"])
        self.assertEqual(codigo, 7)
        self.assertEqual(json.loads(salida.getvalue())["error"]["codigo"], "tiempo_agotado")

    def test_salida_invalida_del_worker(self):
        for texto in ["aviso\n{}", "[]"]:
            salida = StringIO()
            with patch("moodle_bridge.subprocess.run", return_value=Mock(stdout=texto, returncode=0)), redirect_stdout(salida):
                codigo = bridge.main(["--tema", "SQL"])
            self.assertEqual(codigo, 6)
            self.assertEqual(json.loads(salida.getvalue())["error"]["codigo"], "salida_invalida")

    def test_ejecucion_real_del_puente_con_catalogo_de_prueba(self):
        base = Path(__file__).resolve().parent.parent
        antes = (base / "data/interacciones_demo.json").read_bytes()
        proceso = subprocess.run([sys.executable, str(base / "moodle_bridge.py"), "--tema", "bases de datos",
                                  "--fuente", "simulado", "--metodo", "textual"],
                                 cwd="/tmp", capture_output=True, text=True, check=True)
        datos = json.loads(proceso.stdout)
        self.assertTrue(datos["resultados"])
        self.assertEqual(datos["datos"], "simulados")
        self.assertEqual(antes, (base / "data/interacciones_demo.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
