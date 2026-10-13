import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from .tools import buscar_comics_similares

# 1. Inicializamos tu modelo
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
)

# 2. Herramientas disponibles
tools = [buscar_comics_similares]

# 3. Instrucciones del Sistema
system_prompt = """
Eres un asistente experto en cómics independientes. Tu objetivo es ayudar a los lectores a descubrir nuevas historias en nuestra plataforma.
SIEMPRE que te pregunten por cómics, recomendaciones o géneros, usa la herramienta de búsqueda en la base de datos antes de responder. Nunca inventes títulos.
Responde de forma concisa y amigable.
"""

# 4. Agente moderno (se encarga del bucle ReAct automáticamente)
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)

def get_agent_response(user_message: str) -> str:
    """Envía el mensaje al agente y retorna la respuesta final."""
    try:
        # El agente moderno recibe el historial como una lista de mensajes
        result = agent.invoke({
            "messages": [("user", user_message)]
        })
        # El último mensaje de la conversación contiene la respuesta redactada
        return result["messages"][-1].content
    except Exception as e:
        print(f"Error en el agente IA: {e}")
        return "Lo siento, tuve un problema interno al buscar en el catálogo."
