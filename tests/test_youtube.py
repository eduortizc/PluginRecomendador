"""
test_youtube.py – Pruebas unitarias para la integración de YouTube Data API (E2).

Verifica el comportamiento de recuperación de candidatos, lectura de claves,
manejo de respuestas de YouTube, gestión de errores (cuotas, red, respuestas vacías)
y enriquecimiento con estadísticas (vistas, likes, duración).
"""

import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from recomendador.youtube import (
    ErrorYouTube,
    buscar_videos_youtube,
    obtener_clave_api,
    _parsear_duracion_iso8601,
    _enriquecer_con_estadisticas,
)


class TestObtenerClaveApi(unittest.TestCase):

    def test_clave_desde_variable_entorno(self):
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "AIzaFakeEnvKey123"}):
            clave = obtener_clave_api()
            self.assertEqual(clave, "AIzaFakeEnvKey123")

    def test_clave_desde_archivo_env_formato_estandar(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("YOUTUBE_API_KEY=AIzaFileStandard456\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                # Asegurar que no esté en el entorno
                if "YOUTUBE_API_KEY" in os.environ:
                    del os.environ["YOUTUBE_API_KEY"]
                clave = obtener_clave_api(ruta_env=env_file)
                self.assertEqual(clave, "AIzaFileStandard456")

    def test_clave_desde_archivo_env_formato_directo_con_comentarios(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("AIzaDirectKey789 // api key de prueba\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                if "YOUTUBE_API_KEY" in os.environ:
                    del os.environ["YOUTUBE_API_KEY"]
                clave = obtener_clave_api(ruta_env=env_file)
                self.assertEqual(clave, "AIzaDirectKey789")

    def test_sin_clave_lanza_error_especifico(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("# archivo vacío\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                if "YOUTUBE_API_KEY" in os.environ:
                    del os.environ["YOUTUBE_API_KEY"]
                with self.assertRaises(ErrorYouTube) as ctx:
                    obtener_clave_api(ruta_env=env_file)
                self.assertEqual(ctx.exception.codigo, "clave_no_encontrada")


class TestParsearDuracionISO8601(unittest.TestCase):
    """Pruebas para la conversión de duración ISO 8601."""

    def test_minutos_y_segundos(self):
        texto, seg = _parsear_duracion_iso8601("PT12M45S")
        self.assertEqual(texto, "12:45")
        self.assertEqual(seg, 765)

    def test_solo_segundos(self):
        texto, seg = _parsear_duracion_iso8601("PT30S")
        self.assertEqual(texto, "0:30")
        self.assertEqual(seg, 30)

    def test_horas_minutos_segundos(self):
        texto, seg = _parsear_duracion_iso8601("PT1H2M3S")
        self.assertEqual(texto, "1:02:03")
        self.assertEqual(seg, 3723)

    def test_solo_minutos(self):
        texto, seg = _parsear_duracion_iso8601("PT5M")
        self.assertEqual(texto, "5:00")
        self.assertEqual(seg, 300)

    def test_cadena_vacia(self):
        texto, seg = _parsear_duracion_iso8601("")
        self.assertEqual(texto, "0:00")
        self.assertEqual(seg, 0)

    def test_formato_invalido(self):
        texto, seg = _parsear_duracion_iso8601("invalido")
        self.assertEqual(texto, "0:00")
        self.assertEqual(seg, 0)

    def test_una_hora_exacta(self):
        texto, seg = _parsear_duracion_iso8601("PT1H")
        self.assertEqual(texto, "1:00:00")
        self.assertEqual(seg, 3600)


class TestBuscarVideosYouTube(unittest.TestCase):

    def setUp(self):
        self.api_key = "AIzaTestKey_000000"

    def _mock_search_response(self):
        """Respuesta simulada de search.list."""
        return {
            "items": [
                {
                    "id": {"videoId": "vid_001"},
                    "snippet": {
                        "title": "Tutorial de &quot;Python&quot; desde Cero",
                        "description": "Aprende programaci&oacute;n y algoritmos bsicos.",
                        "channelTitle": "Canal Educativo",
                        "publishedAt": "2026-01-15T10:00:00Z",
                    },
                },
                {
                    "id": {"videoId": "vid_002"},
                    "snippet": {
                        "title": "Bases de Datos con Python",
                        "description": "SQL y conexiones prcticas.",
                        "channelTitle": "Dev Tutoriales",
                        "publishedAt": "2026-02-20T12:00:00Z",
                    },
                },
            ]
        }

    def _mock_videos_response(self):
        """Respuesta simulada de videos.list (estadísticas y duración)."""
        return {
            "items": [
                {
                    "id": "vid_001",
                    "statistics": {
                        "viewCount": "150000",
                        "likeCount": "4200",
                    },
                    "contentDetails": {
                        "duration": "PT12M45S",
                    },
                },
                {
                    "id": "vid_002",
                    "statistics": {
                        "viewCount": "85000",
                        "likeCount": "1800",
                    },
                    "contentDetails": {
                        "duration": "PT1H5M30S",
                    },
                },
            ]
        }

    @patch("urllib.request.urlopen")
    def test_busqueda_exitosa_con_enriquecimiento(self, mock_urlopen):
        """Verifica que search.list + videos.list devuelve stats completos."""
        # Primera llamada: search.list; segunda: videos.list
        mock_search = MagicMock()
        mock_search.read.return_value = json.dumps(self._mock_search_response()).encode("utf-8")
        mock_search.__enter__ = MagicMock(return_value=mock_search)
        mock_search.__exit__ = MagicMock(return_value=False)

        mock_videos = MagicMock()
        mock_videos.read.return_value = json.dumps(self._mock_videos_response()).encode("utf-8")
        mock_videos.__enter__ = MagicMock(return_value=mock_videos)
        mock_videos.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [mock_search, mock_videos]

        resultados = buscar_videos_youtube("python", max_resultados=2, api_key=self.api_key)

        self.assertEqual(len(resultados), 2)

        primero = resultados[0]
        self.assertEqual(primero["id"], "vid_001")
        self.assertEqual(primero["titulo"], 'Tutorial de "Python" desde Cero')
        self.assertEqual(primero["canal"], "Canal Educativo")
        self.assertEqual(primero["origen"], "youtube")
        self.assertEqual(primero["url"], "https://www.youtube.com/watch?v=vid_001")
        self.assertEqual(primero["vistas"], 150000)
        self.assertEqual(primero["likes"], 4200)
        self.assertEqual(primero["duracion"], "12:45")
        self.assertEqual(primero["duracion_segundos"], 765)

        segundo = resultados[1]
        self.assertEqual(segundo["vistas"], 85000)
        self.assertEqual(segundo["likes"], 1800)
        self.assertEqual(segundo["duracion"], "1:05:30")
        self.assertEqual(segundo["duracion_segundos"], 3930)

        # Verificar que se hicieron 2 llamadas (search + videos)
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("urllib.request.urlopen")
    def test_busqueda_sin_enriquecimiento(self, mock_urlopen):
        """Con enriquecer=False, solo se hace search.list."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(self._mock_search_response()).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        resultados = buscar_videos_youtube(
            "python", max_resultados=2, api_key=self.api_key, enriquecer=False
        )

        self.assertEqual(len(resultados), 2)
        # No debe tener campos de stats
        self.assertNotIn("vistas", resultados[0])
        # Solo una llamada (search.list)
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("urllib.request.urlopen")
    def test_enriquecimiento_falla_no_pierde_resultados(self, mock_urlopen):
        """Si videos.list falla, los candidatos se devuelven con stats=None."""
        mock_search = MagicMock()
        mock_search.read.return_value = json.dumps(self._mock_search_response()).encode("utf-8")
        mock_search.__enter__ = MagicMock(return_value=mock_search)
        mock_search.__exit__ = MagicMock(return_value=False)

        # Segunda llamada falla
        mock_urlopen.side_effect = [
            mock_search,
            urllib.error.URLError("Network error"),
        ]

        resultados = buscar_videos_youtube("python", max_resultados=2, api_key=self.api_key)

        # Resultados presentes pero sin stats
        self.assertEqual(len(resultados), 2)
        self.assertEqual(resultados[0]["id"], "vid_001")
        self.assertIsNone(resultados[0]["vistas"])
        self.assertIsNone(resultados[0]["likes"])
        self.assertIsNone(resultados[0]["duracion"])

    @patch("urllib.request.urlopen")
    def test_busqueda_sin_resultados(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"items": []}).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        resultados = buscar_videos_youtube("tema_extremadamente_raro_sin_videos", api_key=self.api_key)
        self.assertEqual(resultados, [])

    def test_tema_vacio_lanza_value_error(self):
        with self.assertRaises(ValueError):
            buscar_videos_youtube("   ", api_key=self.api_key)

    @patch("urllib.request.urlopen")
    def test_error_cuota_excedida(self, mock_urlopen):
        err_body = json.dumps({
            "error": {
                "errors": [{"reason": "quotaExceeded", "message": "The request cannot be completed because you have exceeded your quota."}],
                "code": 403,
                "message": "Quota exceeded",
            }
        }).encode("utf-8")

        mock_http_error = urllib.error.HTTPError(
            url="https://www.googleapis.com/youtube/v3/search",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=MagicMock(read=MagicMock(return_value=err_body)),
        )
        mock_urlopen.side_effect = mock_http_error

        with self.assertRaises(ErrorYouTube) as ctx:
            buscar_videos_youtube("python", api_key=self.api_key)
        self.assertEqual(ctx.exception.codigo, "cuota_excedida")

    @patch("urllib.request.urlopen")
    def test_error_peticion_invalida_400(self, mock_urlopen):
        err_body = json.dumps({
            "error": {
                "errors": [{"reason": "keyInvalid", "message": "Bad Request"}],
                "code": 400,
                "message": "API key not valid.",
            }
        }).encode("utf-8")

        mock_http_error = urllib.error.HTTPError(
            url="https://www.googleapis.com/youtube/v3/search",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=MagicMock(read=MagicMock(return_value=err_body)),
        )
        mock_urlopen.side_effect = mock_http_error

        with self.assertRaises(ErrorYouTube) as ctx:
            buscar_videos_youtube("python", api_key=self.api_key)
        self.assertEqual(ctx.exception.codigo, "peticion_invalida")

    @patch("urllib.request.urlopen")
    def test_error_red_urlerror(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Network unreachable")

        with self.assertRaises(ErrorYouTube) as ctx:
            buscar_videos_youtube("python", api_key=self.api_key)
        self.assertEqual(ctx.exception.codigo, "error_red")

    @patch("urllib.request.urlopen")
    def test_error_tiempo_agotado(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError()

        with self.assertRaises(ErrorYouTube) as ctx:
            buscar_videos_youtube("python", api_key=self.api_key)
        self.assertEqual(ctx.exception.codigo, "tiempo_agotado")

    @patch("urllib.request.urlopen")
    def test_error_servicio_503(self, mock_urlopen):
        err_body = b"Service Unavailable"
        mock_http_error = urllib.error.HTTPError(
            url="https://www.googleapis.com/youtube/v3/search",
            code=503,
            msg="Service Unavailable",
            hdrs=None,
            fp=MagicMock(read=MagicMock(return_value=err_body)),
        )
        mock_urlopen.side_effect = mock_http_error

        with self.assertRaises(ErrorYouTube) as ctx:
            buscar_videos_youtube("python", api_key=self.api_key)
        self.assertEqual(ctx.exception.codigo, "servicio_no_disponible")


class TestEnriquecerConEstadisticas(unittest.TestCase):
    """Pruebas directas de _enriquecer_con_estadisticas."""

    def test_lista_vacia_no_hace_llamada(self):
        resultado = _enriquecer_con_estadisticas([], "key_fake")
        self.assertEqual(resultado, [])

    @patch("urllib.request.urlopen")
    def test_id_parcial_no_encontrado(self, mock_urlopen):
        """Si videos.list no devuelve un ID, ese candidato queda con None."""
        candidatos = [
            {"id": "vid_a", "titulo": "A"},
            {"id": "vid_b", "titulo": "B"},
        ]
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "items": [
                {
                    "id": "vid_a",
                    "statistics": {"viewCount": "100", "likeCount": "10"},
                    "contentDetails": {"duration": "PT5M"},
                },
                # vid_b no está en la respuesta
            ]
        }).encode("utf-8")
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        resultado = _enriquecer_con_estadisticas(candidatos, "key_fake")
        self.assertEqual(resultado[0]["vistas"], 100)
        self.assertEqual(resultado[0]["likes"], 10)
        self.assertEqual(resultado[0]["duracion"], "5:00")
        self.assertIsNone(resultado[1]["vistas"])
        self.assertIsNone(resultado[1]["likes"])


if __name__ == "__main__":
    unittest.main()
