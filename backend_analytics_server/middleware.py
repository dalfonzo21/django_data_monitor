import logging
from django.http import JsonResponse, HttpResponse
from django.db import DatabaseError

logger = logging.getLogger(__name__)


class DatabaseErrorMiddleware:
    """
    Middleware para manejar errores de base de datos sin que causen 500.
    Útil en Vercel donde SQLite no persiste entre despliegues.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except DatabaseError as e:
            logger.error(f"Database error on {request.method} {request.path}: {str(e)}")
            # Para POST requests, retornar un error más descriptivo
            if request.method == 'POST':
                return HttpResponse(
                    "Error: Database connection failed. Please try again later.",
                    status=503
                )
            # Para GET requests, retornar error genérico
            return HttpResponse(
                "Service temporarily unavailable.",
                status=503
            )
        return response
