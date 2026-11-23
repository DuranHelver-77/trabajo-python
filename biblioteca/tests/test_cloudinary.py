"""Pruebas unitarias para el servicio de Cloudinary."""
import io
import pytest
from unittest.mock import patch
from fastapi import UploadFile

from app.core.cloudinary import subir_imagen_libro, eliminar_imagen
from app.core.exceptions import ReglaNegocio


def crear_upload_file(nombre: str, contenido: bytes, content_type: str) -> UploadFile:
    return UploadFile(filename=nombre, file=io.BytesIO(contenido), headers={"content-type": content_type})


def test_archivo_tipo_invalido():
    archivo = crear_upload_file("archivo.txt", b"hola mundo", "text/plain")
    with patch("app.core.cloudinary.settings.cloudinary_cloud_name", "test_cloud"):
        with patch("app.core.cloudinary.settings.cloudinary_api_key", "test_key"):
            with patch("app.core.cloudinary.settings.cloudinary_api_secret", "test_secret"):
                with pytest.raises(ReglaNegocio, match="Formato no soportado"):
                    subir_imagen_libro(archivo)


def test_archivo_demasiado_grande():
    contenido_pesado = b"0" * (6 * 1024 * 1024)  # 6 MB
    archivo = crear_upload_file("foto.jpg", contenido_pesado, "image/jpeg")
    with patch("app.core.cloudinary.settings.cloudinary_cloud_name", "test_cloud"):
        with patch("app.core.cloudinary.settings.cloudinary_api_key", "test_key"):
            with patch("app.core.cloudinary.settings.cloudinary_api_secret", "test_secret"):
                with pytest.raises(ReglaNegocio, match="no debe superar los 5 MB"):
                    subir_imagen_libro(archivo)


def test_error_sin_credenciales():
    archivo = crear_upload_file("foto.jpg", b"dummy", "image/jpeg")
    with patch("app.core.cloudinary.settings.cloudinary_cloud_name", ""):
        with pytest.raises(ReglaNegocio, match="Cloudinary no está configurado"):
            subir_imagen_libro(archivo)


def test_subida_exitosa_mock():
    archivo = crear_upload_file("foto.png", b"imagen_valida", "image/png")
    mock_response = {
        "secure_url": "https://res.cloudinary.com/test/image/upload/v1234/test.png",
        "public_id": "biblioteca/portadas/test",
    }
    with patch("app.core.cloudinary.settings.cloudinary_cloud_name", "test_cloud"):
        with patch("app.core.cloudinary.settings.cloudinary_api_key", "test_key"):
            with patch("app.core.cloudinary.settings.cloudinary_api_secret", "test_secret"):
                with patch("cloudinary.uploader.upload", return_value=mock_response):
                    url, public_id = subir_imagen_libro(archivo)
                    assert url == mock_response["secure_url"]
                    assert public_id == mock_response["public_id"]


def test_eliminar_imagen_mock():
    with patch("app.core.cloudinary.settings.cloudinary_cloud_name", "test_cloud"):
        with patch("cloudinary.uploader.destroy") as mock_destroy:
            eliminar_imagen("biblioteca/portadas/test")
            mock_destroy.assert_called_once_with("biblioteca/portadas/test")

