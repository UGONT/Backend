# assistant/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services import get_agent_response
from django.contrib.auth.models import User


# ⚠️ TEMPORAL: usuario hardcodeado para testear sin auth
USUARIO_TEST_USERNAME = 'Hugo'   # 👈 cambiá por el username real que quieras


def _get_usuario_test():
    """Devuelve el usuario de pruebas. Cambiar por request.user cuando haya auth."""
    try:
        return User.objects.get(username=USUARIO_TEST_USERNAME)
    except User.DoesNotExist:
        return None


@api_view(['POST'])
def chat_view(request):
    """
    POST /api/assistant/chat/
    Body: { "mensaje": "recomiéndame algo" }
    Respuesta: { "respuesta": "...", "user_id": 1 }
    """
    mensaje = request.data.get('mensaje', '').strip()
    if not mensaje:
        return Response(
            {"error": "El campo 'mensaje' es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    usuario = _get_usuario_test()
    user_id = usuario.id if usuario else None

    respuesta = get_agent_response(mensaje, user_id=user_id)

    return Response({
        "respuesta": respuesta,
        "user_id": user_id,
    })