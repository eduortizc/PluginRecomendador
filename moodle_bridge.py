"""Entrada JSON para el plugin Moodle. No requiere un servidor HTTP.

El proceso padre limita la duración del trabajador; stdout contiene solo JSON.
La fuente simulada se conserva exclusivamente para las pruebas automatizadas.
"""

import argparse
from contextlib import redirect_stdout
import json
import os
from pathlib import Path
import subprocess
import sys


def error(codigo, mensaje):
    return {"error": {"codigo": codigo, "mensaje": mensaje}}


def ejecutar(args):
    """Ejecuta las funciones existentes sin registrar usuarios ni interacciones."""
    if not args.tema.strip() or len(args.tema) > 500:
        return error("entrada_invalida", "Escribe un tema de entre 1 y 500 caracteres."), 2
    if args.cache_dir:
        os.environ["HF_HOME"] = str(Path(args.cache_dir).expanduser())

    # Algunas dependencias imprimen avisos; nunca deben mezclarse con el JSON.
    with redirect_stdout(sys.stderr):
        from recomendador.catalogo import cargar_catalogo, ErrorCatalogo
        from recomendador.youtube import buscar_videos_youtube, ErrorYouTube
        from recomendador.ranking import recomendar

        try:
            if args.fuente == "youtube":
                candidatos = buscar_videos_youtube(
                    args.tema.strip(), max_resultados=args.max_candidatos,
                    timeout=min(15, args.timeout),
                )
            else:
                candidatos = cargar_catalogo()
            respuesta = recomendar(
                args.tema.strip(), candidatos, limite=args.limite, metodo=args.metodo,
            )
            # Incluso una respuesta vacía conserva la fuente que se consultó.
            respuesta["datos"] = "youtube" if args.fuente == "youtube" else "simulados"
            respuesta["texto_analizado"] = ["titulo", "descripcion"]
            return respuesta, 0
        except ErrorYouTube as exc:
            # No enviar al navegador URLs de error que puedan contener la clave.
            return error(exc.codigo, "No se pudo completar la consulta a YouTube."), 3
        except ImportError:
            return error("dependencias", "Faltan dependencias en el Python configurado."), 4
        except ErrorCatalogo:
            return error("catalogo", "No se pudo leer el catálogo de prueba."), 5
        except Exception:
            return error("motor", "No se pudo cargar el modelo o completar el análisis."), 6


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tema", required=True)
    parser.add_argument("--fuente", choices=["youtube", "simulado"], default="youtube")
    parser.add_argument("--metodo", choices=["textual", "semantico"], default="semantico")
    parser.add_argument("--limite", type=int, choices=range(1, 6), default=5)
    parser.add_argument("--max-candidatos", type=int, choices=range(1, 51), default=20)
    parser.add_argument("--timeout", type=int, choices=range(1, 601), default=120)
    parser.add_argument("--cache-dir", default="")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    argumentos = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(argumentos)
    if args.worker:
        datos, codigo = ejecutar(args)
    else:
        comando = [sys.executable, str(Path(__file__).resolve()), *argumentos, "--worker"]
        try:
            resultado = subprocess.run(
                comando, capture_output=True, text=True, encoding="utf-8",
                timeout=args.timeout, check=False,
            )
            try:
                datos = json.loads(resultado.stdout)
                if not isinstance(datos, dict):
                    raise ValueError("La salida no es un objeto JSON")
                codigo = resultado.returncode
                if codigo != 0 and not isinstance(datos.get("error"), dict):
                    datos = error("motor", "El proceso de análisis terminó con un error.")
                elif codigo == 0 and "error" in datos:
                    codigo = 6
            except (ValueError, TypeError):
                datos, codigo = error("salida_invalida", "El motor no devolvió JSON válido."), 6
        except subprocess.TimeoutExpired:
            datos, codigo = error("tiempo_agotado", "Se agotó el tiempo de análisis."), 7
        except OSError:
            datos, codigo = error("motor", "No se pudo iniciar el proceso de análisis."), 6
    print(json.dumps(datos, ensure_ascii=False, allow_nan=False))
    return codigo


if __name__ == "__main__":
    sys.exit(main())
