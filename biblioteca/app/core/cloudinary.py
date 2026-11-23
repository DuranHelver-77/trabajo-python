"""
Módulo de integración con Cloudinary para subida y eliminación de imágenes.
"""
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import ReglaNegocio

settings = get_settings()

if settings.cloudinary_cloud_name:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
MAX_TAMANIO_BYTES = 5 * 1024 * 1024  # 5 MB


def subir_imagen_libro(archivo: UploadFile) -> tuple[str, str]:
    """
    Valida el archivo y lo sube a Cloudinary en la carpeta 'biblioteca/portadas'.
    Retorna una tupla: (secure_url, public_id).
    """
    if not (settings.cloudinary_cloud_name and settings.cloudinary_api_key and settings.cloudinary_api_secret):
        raise ReglaNegocio(
            "Cloudinary no está configurado. Configura CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET en tu archivo .env."
        )

    # 1. Validar tipo de contenido
    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise ReglaNegocio("Formato no soportado. El archivo debe ser una imagen JPEG, PNG o WEBP.")

    # 2. Validar tamaño del archivo
    archivo.file.seek(0, 2)
    tamanio = archivo.file.tell()
    archivo.file.seek(0)
    if tamanio > MAX_TAMANIO_BYTES:
        raise ReglaNegocio("La imagen no debe superar los 5 MB.")

    try:
        resultado = cloudinary.uploader.upload(
            archivo.file,
            folder="biblioteca/portadas",
            resource_type="image",
            transformation=[
                {"width": 800, "height": 1200, "crop": "limit"},
                {"quality": "auto", "fetch_format": "auto"},
            ],
        )
        secure_url = resultado.get("secure_url")
        public_id = resultado.get("public_id")
        if not secure_url or not public_id:
            raise ReglaNegocio("Respuesta inesperada al subir imagen a Cloudinary.")
        return secure_url, public_id
    except Exception as e:
        if isinstance(e, ReglaNegocio):
            raise
        raise ReglaNegocio(f"Error al subir imagen a Cloudinary: {str(e)}")


def eliminar_imagen(public_id: str | None) -> None:
    """Elimina la imagen de Cloudinary si cuenta con un public_id válido."""
    if not public_id or not settings.cloudinary_cloud_name:
        return
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception:
        # No bloquear operaciones si Cloudinary falla al limpiar imagen anterior
        pass

