from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import get_agent_response

class ChatAgentView(APIView):
    def post(self, request):
        user_message = request.data.get("message")
        
        if not user_message:
            return Response(
                {"error": "El campo 'message' es obligatorio."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Llamamos a nuestro servicio de LangChain
        ai_response = get_agent_response(user_message)
        
        return Response({"response": ai_response}, status=status.HTTP_200_OK)

