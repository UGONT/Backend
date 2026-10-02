from django.urls import path
from .views import ChatAgentView

urlpatterns = [
    path('chat/', ChatAgentView.as_view(), name='chat_agent'),
]