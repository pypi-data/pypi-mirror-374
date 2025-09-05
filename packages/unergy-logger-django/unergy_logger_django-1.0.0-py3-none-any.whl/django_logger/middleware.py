import threading
import time

from django.http import HttpRequest, HttpResponse

from .constants import AuditAction, AuditLevel
from .models import AuditLog
from .utils import AuditDataSerializer

_user = threading.local()


def get_current_user():
    """Obtiene el usuario del hilo actual."""
    return getattr(_user, "value", None)


class LoggerMiddleware:
    """
    Middleware principal para logging automático de requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Almacenar el usuario actual en el hilo local
        _user.value = request.user if request.user.is_authenticated else None

        # Registrar tiempo de inicio
        start_time = time.time()

        # Procesar la request
        response = self.get_response(request)

        # Calcular duración
        duration = time.time() - start_time

        # Registrar la request en el log
        self._log_request(request, response, duration)

        return response

    def _log_request(
        self,
        request: HttpRequest,
        response: HttpResponse,
        duration: float,
    ) -> None:
        """Registra la request en el sistema de logging."""
        # Determinar el nivel basado en el código de respuesta
        level = self._get_level_from_status(response.status_code)

        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=AuditAction.READ,
            level=level,
            description=f"HTTP {request.method} {request.path}",
            request_data=AuditDataSerializer.serialize_request(request),
            response_data=AuditDataSerializer.serialize_response(response),
            ip_address=request.META.get("REMOTE_ADDR"),
            duration=duration,
            status_code=response.status_code,
            method=request.method,
            path=request.path,
        )

    def _get_level_from_status(self, status_code: int) -> str:
        """Determina el nivel de logging basado en el código de estado HTTP."""
        if status_code < 400:
            return AuditLevel.LOW
        elif status_code < 500:
            return AuditLevel.MEDIUM
        else:
            return AuditLevel.HIGH
