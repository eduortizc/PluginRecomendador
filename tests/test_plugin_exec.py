"""Ejecuta el conector PHP real cuando PHP_BINARY o php están disponibles."""
import os
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PHP = os.environ.get("PHP_BINARY") or shutil.which("php")


@unittest.skipUnless(PHP, "PHP no disponible; ejecutar con PHP_BINARY=/ruta/php")
class TestPluginExec(unittest.TestCase):
    def test_endpoint_no_admite_suplantacion_csrf_ni_videos_ajenos(self):
        root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            destino = fixture / "blocks/videorec"
            shutil.copytree(root / "moodle_plugin/videorec", destino)
            shutil.copy(root / "tests/php/rating_bootstrap.php", fixture / "config.php")
            for caso in ("valid", "other-course", "unseen-video", "csrf", "range", "get", "guest", "no-access"):
                with self.subTest(caso=caso):
                    proceso = subprocess.run([PHP, "-n", str(root / "tests/php/rating_endpoint_smoke.php"),
                                              str(fixture), caso], capture_output=True, text=True, timeout=10)
                    self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
                    self.assertIn("Rating endpoint OK", proceso.stdout)

    def test_php_exec_hibrido_contexto_temporal_y_respaldo(self):
        root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory(prefix="videorec híbrido '") as temporal:
            fixture = Path(temporal)
            proyecto = fixture / "proyecto"
            proyecto.mkdir()
            shutil.copy(root / "moodle_bridge.py", proyecto)
            for carpeta in ["recomendador", "moodle_plugin"]:
                shutil.copytree(root / carpeta, proyecto / carpeta)
            (proyecto / "data").mkdir()
            candidatos = [{"id": v, "titulo": "Prueba ficticia", "descripcion": "SQL",
                           "origen": "simulado", "url": None}
                          for v in ("AAAAAAA0001", "BBBBBBB0002", "CCCCCCC0003", "DDDDDDD0004")]
            (proyecto / "data/videos_demo.json").write_text(json.dumps({"videos": candidatos}))
            # Controlled embeddings only in the temporary fixture, never in shipped code.
            (proyecto / "sentence_transformers.py").write_text(
                "import math\nclass SentenceTransformer:\n"
                "    def __init__(self, *args, **kwargs): pass\n"
                "    def encode(self, textos, **kwargs):\n"
                "        scores=[.8,.7,.01,.5][:len(textos)-1]\n"
                "        return [[1.,0.]]+[[s,math.sqrt(1-s*s)] for s in scores]\n")
            proceso = subprocess.run([PHP, "-n", str(root / "tests/php/hybrid_smoke.php"),
                                      str(proyecto), sys.executable, str(fixture)],
                                     capture_output=True, text=True, timeout=40)
        self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
        self.assertIn("PHP hybrid integration OK", proceso.stdout)

    def test_php_exec_y_presentacion(self):
        root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory(prefix="videorec espacio ' ") as temporal:
            fixture = Path(temporal)
            # A quoted executable path checks that PHP quotes the whole path.
            interprete = fixture / "python con espacios"
            interprete.symlink_to(sys.executable)
            # Exercise the actual bridge under a project path with quotes/spaces too.
            proyecto = fixture / "proyecto con espacios"
            proyecto.mkdir()
            shutil.copy(root / "moodle_bridge.py", proyecto)
            for carpeta in ["recomendador", "data", "moodle_plugin"]:
                shutil.copytree(root / carpeta, proyecto / carpeta)
            proceso = subprocess.run([PHP, "-n", str(root / "tests/php/connector_smoke.php"),
                                      str(proyecto), str(interprete), str(fixture)],
                                     capture_output=True, text=True, timeout=40)
        self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
        self.assertIn("PHP exec integration OK", proceso.stdout)
