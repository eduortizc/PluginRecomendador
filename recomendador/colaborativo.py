"""Filtrado colaborativo por vecinos de usuario sobre valoraciones explícitas.

No utiliza vistas, likes de YouTube ni impresiones como preferencias. La matriz
contiene valores de 1 a 5; las ausencias son desconocidas, no valoraciones cero.
"""

import math


def predecir_colaborativo(usuario_id, video_ids, matriz, max_vecinos=10,
                         min_comunes=2):
    """Predice afinidad [0, 1] con coseno sobre videos valorados en común.

    Exige dos videos comunes por defecto. Los vecinos se ordenan por similitud;
    para cada candidato se usan hasta diez que lo hayan valorado. El promedio
    ponderado en escala 1-5 se normaliza con (valor-1)/4. Sin evidencia devuelve
    None por video, acompañado de un motivo explícito para recurrir a contenido.
    """
    if max_vecinos < 1 or min_comunes < 1:
        raise ValueError("Los límites de vecinos y coincidencias deben ser positivos.")
    for valoraciones in matriz.values():
        for valor in valoraciones.values():
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor) or not 1 <= valor <= 5:
                raise ValueError("La matriz requiere valoraciones finitas entre 1 y 5.")

    objetivo = matriz.get(usuario_id, {}) if usuario_id else {}
    vecinos = []
    for otro_id, valoraciones in matriz.items():
        if otro_id == usuario_id:
            continue
        comunes = sorted(objetivo.keys() & valoraciones.keys())
        if len(comunes) < min_comunes:
            continue
        numerador = sum(objetivo[v] * valoraciones[v] for v in comunes)
        norma = math.sqrt(sum(objetivo[v] ** 2 for v in comunes)) * math.sqrt(
            sum(valoraciones[v] ** 2 for v in comunes))
        similitud = numerador / norma
        vecinos.append((similitud, otro_id, valoraciones))
    vecinos.sort(key=lambda v: (-v[0], v[1]))

    predicciones = {}
    for video_id in video_ids:
        disponibles = [v for v in vecinos if video_id in v[2]][:max_vecinos]
        motivo = None
        if not usuario_id:
            motivo = "sin_usuario"
        elif not objetivo:
            motivo = "usuario_sin_valoraciones"
        elif not vecinos:
            motivo = "sin_vecinos_suficientes"
        elif not disponibles:
            motivo = "video_sin_valoraciones_de_vecinos"
        score = None
        if disponibles:
            valor = sum(s * vals[video_id] for s, _, vals in disponibles) / sum(
                s for s, _, _ in disponibles)
            score = max(0.0, min(1.0, (valor - 1.0) / 4.0))
        predicciones[video_id] = {
            "puntuacion_colaborativa": score,
            "vecinos_utilizados": len(disponibles),
            "motivo_respaldo": motivo,
        }
    return predicciones
