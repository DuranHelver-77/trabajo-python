"""
Instancia compartida del rate limiter (slowapi).

Se separa de main.py para evitar imports circulares:
  main.py → routes/auth.py → limiter.py  (sin ciclo)
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

_settings = get_settings()

# En entorno test el limiter se construye desactivado para que no
# interfiera con los tests (pytest-env inyecta ENVIRONMENT=test antes
# de cargar cualquier módulo de la app).
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    enabled=(_settings.environment != "test"),
)
