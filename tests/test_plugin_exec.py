"""Ejecuta el conector PHP real cuando PHP_BINARY o php están disponibles."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PHP = os.environ.get("PHP_BINARY") or shutil.which("php")


@unittest.skipUnless(PHP, "PHP no disponible; ejecutar con PHP_BINARY=/ruta/php")
class TestPluginExec(unittest.TestCase):
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
