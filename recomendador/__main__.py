"""
__main__.py – Entrada de consola del recomendador.

Uso:
    python3 -m recomendador --tema "bases de datos"
    python3 -m recomendador --tema "bases de datos" --metodo semantico
    python3 -m recomendador --tema "bases de datos" --metodo hibrido --fuente youtube
    python3 -m recomendador --tema "bases de datos" --nivel introductorio --usuario usr_estudiante_01
    python3 -m recomendador --ver-matriz
    python3 -m recomendador --listar-usuarios
    python3 -m recomendador --web
"""

import argparse
import json
import sys

from .catalogo import cargar_catalogo, ErrorCatalogo
from .ranking import recomendar
from .youtube import buscar_videos_youtube, ErrorYouTube
from .visualizador import exportar_y_abrir
from .interacciones import GestorInteracciones, ErrorInteraccion


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recomendador de videos educativos – E1/E2/E3/E4.",
    )
    parser.add_argument(
        "--tema",
        required=False,
        help="Tema de búsqueda (texto libre). Obligatorio salvo al usar --web, --ver-matriz o --listar-usuarios.",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=5,
        help="Cantidad máxima de resultados devueltos (1-5, por defecto 5).",
    )
    parser.add_argument(
        "--fuente",
        choices=["simulado", "youtube"],
        default="simulado",
        help="Origen de los candidatos: 'simulado' (catálogo local) o 'youtube' (YouTube Data API v3).",
    )
    parser.add_argument(
        "--metodo",
        choices=["textual", "semantico", "hibrido"],
        default="textual",
        help=(
            "Método de ranking: "
            "'textual' (coincidencia de palabras, E1), "
            "'semantico' (embeddings sentence-transformers, E3), "
            "'hibrido' (combinación ponderada, E3). "
            "Por defecto: textual."
        ),
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.4,
        help=(
            "Peso del componente textual en modo 'hibrido' (0.0–1.0). "
            "Por defecto 0.4 (60 %% semántico, 40 %% textual)."
        ),
    )
    parser.add_argument(
        "--max-candidatos",
        type=int,
        default=10,
        help="Máximo de candidatos a recuperar de la fuente (por defecto 10).",
    )
    parser.add_argument(
        "--usuario",
        type=str,
        default=None,
        help="ID de usuario para contextualizar la búsqueda o registrar señales (E4).",
    )
    parser.add_argument(
        "--nivel",
        choices=["introductorio", "intermedio", "avanzado"],
        default=None,
        help="Nivel didáctico del contexto pedagógico (E4).",
    )
    parser.add_argument(
        "--disciplina",
        type=str,
        default=None,
        help="Disciplina del contexto pedagógico (E4).",
    )
    parser.add_argument(
        "--ver-matriz",
        action="store_true",
        help="Muestra la matriz de utilidad usuario × video generada a partir de las interacciones (E4).",
    )
    parser.add_argument(
        "--listar-usuarios",
        action="store_true",
        help="Lista los perfiles de usuario simulados disponibles (E4).",
    )
    parser.add_argument(
        "--html",
        nargs="?",
        const="recomendaciones.html",
        default=None,
        metavar="ARCHIVO",
        help="Genera un archivo HTML visual interactivo y lo abre en el navegador.",
    )
    parser.add_argument(
        "--web",
        nargs="?",
        const=8080,
        type=int,
        default=None,
        metavar="PUERTO",
        help="Inicia una aplicación web visual interactiva local (por defecto puerto 8080).",
    )

    args = parser.parse_args()

    # ── Modo Servidor Web Interactivo ─────────────────────────────────
    if args.web is not None:
        from .servidor import iniciar_servidor_web
        iniciar_servidor_web(puerto=args.web)
        return

    # ── Listar usuarios (E4) ─────────────────────────────────────────
    if args.listar_usuarios:
        gestor = GestorInteracciones()
        print(json.dumps({"usuarios": gestor.obtener_usuarios()}, ensure_ascii=False, indent=2))
        return

    # ── Ver Matriz de Utilidad (E4) ──────────────────────────────────
    if args.ver_matriz:
        gestor = GestorInteracciones()
        matriz = gestor.generar_matriz_utilidad()
        print(json.dumps({
            "metodo": "matriz_utilidad_interacciones",
            "descripcion": "Puntuaciones consolidadas (explícitas 1-5 e implícitas inferidas)",
            "usuarios": len(matriz),
            "matriz": matriz,
        }, ensure_ascii=False, indent=2))
        return

    # Si no es modo especial, el tema es requerido
    if not args.tema:
        parser.error("El argumento --tema es obligatorio para búsquedas por consola.")

    # ── Validar límite ──────────────────────────────────────────────
    if not 1 <= args.limite <= 5:
        print("Error: --limite debe ser un entero entre 1 y 5.", file=sys.stderr)
        sys.exit(1)

    # ── Validar alpha ───────────────────────────────────────────────
    if not 0.0 <= args.alpha <= 1.0:
        print("Error: --alpha debe ser un número entre 0.0 y 1.0.", file=sys.stderr)
        sys.exit(1)

    # ── Obtener candidatos según la fuente ───────────────────────────
    if args.fuente == "youtube":
        try:
            candidatos = buscar_videos_youtube(
                tema=args.tema,
                max_resultados=args.max_candidatos,
            )
        except ErrorYouTube as exc:
            print(f"Error de YouTube Data API [{exc.codigo}]: {exc}", file=sys.stderr)
            sys.exit(3)
    else:
        try:
            candidatos = cargar_catalogo()
        except ErrorCatalogo as exc:
            print(f"Error de catálogo: {exc}", file=sys.stderr)
            sys.exit(2)

    # ── Construir contexto si se especificó ──────────────────────────
    contexto = {}
    if args.usuario:
        contexto["usuario_id"] = args.usuario
    if args.nivel:
        contexto["nivel"] = args.nivel
    if args.disciplina:
        contexto["disciplina"] = args.disciplina

    # ── Ejecutar recomendación ──────────────────────────────────────
    if args.metodo in ("semantico", "hibrido"):
        print(
            f"⏳ Cargando modelo de embeddings para método '{args.metodo}'...",
            file=sys.stderr,
        )

    resultado = recomendar(
        args.tema,
        candidatos,
        args.limite,
        metodo=args.metodo,
        alpha=args.alpha,
        contexto=contexto or None,
    )

    # Si hay un usuario indicado, registrar evento de 'impresion' de los recomendados
    if args.usuario:
        gestor = GestorInteracciones()
        for r in resultado.get("resultados", []):
            gestor.registrar_evento(
                usuario_id=args.usuario,
                video_id=r["id"],
                tipo="impresion",
                contexto=contexto or None,
            )

    # ── Exportar a vista HTML si se solicitó ────────────────────────
    if args.html:
        ruta_generada = exportar_y_abrir(resultado, args.html)
        print(f"✅ Vista visual HTML generada y abierta en el navegador: {ruta_generada}")

    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
