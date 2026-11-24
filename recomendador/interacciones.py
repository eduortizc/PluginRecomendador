"""
interacciones.py – Gestión de perfiles, contexto e interacciones (E4).

Modelado de usuarios, contexto pedagógico y diferenciación de señales
(impresión, apertura, selección y valoración explícita), con generación
de matriz de utilidad para el filtrado colaborativo (E5).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Tipos de interacción válidos ─────────────────────────────────────────────

TIPO_IMPRESION = "impresion"
TIPO_APERTURA = "apertura"
TIPO_SELECCION = "seleccion"
TIPO_VALORACION = "valoracion"

TIPOS_VALIDOS: frozenset[str] = frozenset({
    TIPO_IMPRESION,
    TIPO_APERTURA,
    TIPO_SELECCION,
    TIPO_VALORACION,
})

# Ponderación por defecto para convertir señales implícitas en escala de utilidad (1-5)
# cuando no existe una valoración explícita del usuario.
PESO_SENALES_IMPLICITAS = {
    TIPO_IMPRESION: 1.0,
    TIPO_APERTURA: 2.5,
    TIPO_SELECCION: 4.0,
}

RUTA_DATOS_DEFECTO = Path(__file__).resolve().parent.parent / "data" / "interacciones_demo.json"


class ErrorInteraccion(Exception):
    """Excepción para errores de validación de perfiles o interacciones."""
    pass


class GestorInteracciones:
    """Administra los perfiles de usuario y el registro de eventos de interacción.

    Permite:
    - Registrar eventos diferenciando impresión, apertura, selección y valoración.
    - Consultar el historial por usuario o por recurso.
    - Generar la matriz de utilidad (usuario × video) requerida para E5.
    """

    def __init__(self, ruta_archivo: Path | str | None = None) -> None:
        self.ruta: Path = Path(ruta_archivo) if ruta_archivo else RUTA_DATOS_DEFECTO
        self.usuarios: dict[str, dict[str, Any]] = {}
        self.eventos: list[dict[str, Any]] = []
        self._contador_eventos: int = 0
        self.cargar()

    # ── Persistencia ─────────────────────────────────────────────────────────

    def cargar(self) -> None:
        """Carga usuarios y eventos desde el archivo JSON si existe."""
        if not self.ruta.exists():
            self.usuarios = {}
            self.eventos = []
            return

        try:
            with open(self.ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            raise ErrorInteraccion(f"No se pudo leer el archivo de interacciones: {exc}") from exc

        self.usuarios = {u["id"]: u for u in datos.get("usuarios", []) if "id" in u}
        self.eventos = datos.get("interacciones", [])
        self._contador_eventos = len(self.eventos)

    def guardar(self, ruta_destino: Path | str | None = None) -> None:
        """Guarda usuarios y eventos en formato JSON."""
        destino = Path(ruta_destino) if ruta_destino else self.ruta
        destino.parent.mkdir(parents=True, exist_ok=True)

        datos = {
            "_nota": "Registro de perfiles e interacciones de Recomendador_Ext.",
            "usuarios": list(self.usuarios.values()),
            "interacciones": self.eventos,
        }

        try:
            with open(destino, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            raise ErrorInteraccion(f"No se pudo guardar el archivo de interacciones: {exc}") from exc

    # ── Perfiles de usuario ──────────────────────────────────────────────────

    def agregar_usuario(
        self,
        usuario_id: str,
        nombre: str,
        rol: str = "estudiante",
        nivel: str = "introductorio",
        disciplinas: list[str] | None = None,
    ) -> dict[str, Any]:
        """Crea o actualiza un perfil de usuario."""
        if not usuario_id or not usuario_id.strip():
            raise ErrorInteraccion("El identificador del usuario no puede estar vacío.")

        usuario = {
            "id": usuario_id.strip(),
            "nombre": nombre.strip(),
            "rol": rol.strip().lower(),
            "nivel": nivel.strip().lower(),
            "disciplinas": [d.strip().lower() for d in (disciplinas or [])],
        }
        self.usuarios[usuario["id"]] = usuario
        return usuario

    def obtener_usuarios(self) -> list[dict[str, Any]]:
        """Devuelve la lista de usuarios registrados."""
        return list(self.usuarios.values())

    def obtener_usuario(self, usuario_id: str) -> dict[str, Any] | None:
        """Busca un usuario por su ID."""
        return self.usuarios.get(usuario_id)

    # ── Registro de interacciones ────────────────────────────────────────────

    def registrar_evento(
        self,
        usuario_id: str,
        video_id: str,
        tipo: str,
        valor: float | None = None,
        contexto: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Registra una interacción con validación estricta de tipo y rango.

        Parámetros
        ----------
        usuario_id : str
            ID del usuario (existente o nuevo).
        video_id : str
            ID del recurso (ej: demo_001 o ID de YouTube).
        tipo : str
            'impresion' | 'apertura' | 'seleccion' | 'valoracion'.
        valor : float | None
            Puntuación explícita (1.0 a 5.0 para 'valoracion').
        contexto : dict | None
            Contexto didáctico (tema, nivel, disciplina).
        """
        if not usuario_id or not usuario_id.strip():
            raise ErrorInteraccion("usuario_id no puede estar vacío.")
        if not video_id or not video_id.strip():
            raise ErrorInteraccion("video_id no puede estar vacío.")

        tipo_norm = tipo.strip().lower()
        if tipo_norm not in TIPOS_VALIDOS:
            raise ErrorInteraccion(
                f"Tipo de interacción '{tipo}' no válido. Opciones: {sorted(TIPOS_VALIDOS)}"
            )

        # Validación específica para valoraciones
        if tipo_norm == TIPO_VALORACION:
            if valor is None:
                raise ErrorInteraccion("La interacción de tipo 'valoracion' requiere un valor numérico.")
            try:
                valor_f = float(valor)
            except (ValueError, TypeError) as exc:
                raise ErrorInteraccion(f"El valor de valoración debe ser numérico: {valor}") from exc

            if not (1.0 <= valor_f <= 5.0):
                raise ErrorInteraccion(
                    f"El valor de valoración debe estar en el rango [1.0, 5.0]. Recibido: {valor_f}"
                )
            valor_final: float | None = round(valor_f, 2)
        else:
            # Para apertura, seleccion e impresion, si se pasa un valor se normaliza o se usa 1.0
            valor_final = float(valor) if valor is not None else 1.0

        self._contador_eventos += 1
        evento_id = f"ev_{self._contador_eventos:04d}"
        timestamp = datetime.now(timezone.utc).isoformat()

        evento = {
            "id": evento_id,
            "usuario_id": usuario_id.strip(),
            "video_id": video_id.strip(),
            "tipo": tipo_norm,
            "valor": valor_final,
            "contexto": contexto or {},
            "timestamp": timestamp,
        }

        self.eventos.append(evento)
        return evento

    def obtener_historial_usuario(self, usuario_id: str) -> list[dict[str, Any]]:
        """Devuelve todos los eventos registrados para un usuario."""
        return [e for e in self.eventos if e["usuario_id"] == usuario_id]

    def obtener_historial_video(self, video_id: str) -> list[dict[str, Any]]:
        """Devuelve todos los eventos registrados para un video."""
        return [e for e in self.eventos if e["video_id"] == video_id]

    # ── Matriz de utilidad para Filtrado Colaborativo (E5) ────────────────────

    def generar_matriz_utilidad(self, solo_valoraciones: bool = False) -> dict[str, dict[str, float]]:
        """Genera una matriz usuario × video con puntuaciones consolidadas en escala 1.0 - 5.0.

        Reglas de consolidación:
        1. Si existe al menos una 'valoracion' explícita del usuario para el video,
           se utiliza el promedio de sus valoraciones explícitas (prioridad máxima).
        2. Si solo existen señales implícitas (seleccion, apertura, impresion),
           se calcula el valor máximo inferido según `PESO_SENALES_IMPLICITAS`.

        Devuelve
        --------
        Con solo_valoraciones=True se excluyen las señales implícitas. Es la
        matriz que utiliza E5; una impresión no significa agrado o desagrado.

        dict[str, dict[str, float]]
            Estructura {usuario_id: {video_id: score_1_a_5}}
        """
        # Agrupar eventos por (usuario_id, video_id)
        agrupados: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for ev in self.eventos:
            if solo_valoraciones and ev["tipo"] != TIPO_VALORACION:
                continue
            clave = (ev["usuario_id"], ev["video_id"])
            agrupados.setdefault(clave, []).append(ev)

        matriz: dict[str, dict[str, float]] = {}

        for (usr, vid), lista_ev in agrupados.items():
            # Revisar si hay valoraciones explícitas
            valoraciones = [
                e["valor"] for e in lista_ev
                if e["tipo"] == TIPO_VALORACION and e.get("valor") is not None
            ]

            if valoraciones:
                # Promedio de ratings explícitos
                score = sum(valoraciones) / len(valoraciones)
            else:
                # Inferencia desde señales implícitas
                pesos = [
                    PESO_SENALES_IMPLICITAS.get(e["tipo"], 1.0)
                    for e in lista_ev
                ]
                score = max(pesos) if pesos else 1.0

            if usr not in matriz:
                matriz[usr] = {}
            matriz[usr][vid] = round(float(score), 2)

        return matriz


