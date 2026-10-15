# assistant/services.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from .tools import (
    buscar_comics_similares,
    buscar_comics_por_estilo_visual,
    buscar_comics_por_autor,
    buscar_comics_por_genero,
    filtrar_comics_por_estado,
    filtrar_comics_por_valoracion,
    filtrar_comics_por_meta,
    obtener_detalle_comic,
)

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
)

tools = [
    buscar_comics_similares,
    buscar_comics_por_estilo_visual,
    buscar_comics_por_autor,
    buscar_comics_por_genero,
    filtrar_comics_por_estado,
    filtrar_comics_por_valoracion,
    filtrar_comics_por_meta,
    obtener_detalle_comic,
]

system_prompt = """
Eres un asistente experto en cómics independientes que ayuda a los lectores
a descubrir nuevas historias en nuestra plataforma de crowdfunding.

## Tu rol
Ayudas a los usuarios a:
1. Encontrar cómics según sus gustos (temática, estilo visual, género).
2. Conocer detalles de cómics específicos (autores, capítulos, recompensas).
3. Explorar el catálogo según su estado de financiamiento.

## Herramientas disponibles
- **buscar_comics_similares**: búsqueda semántica por temática/historia.
  Ej: "algo de piratas", "historia triste", "cyberpunk con romance".
- **buscar_comics_por_estilo_visual**: búsqueda por estilo artístico de la portada.
  Ej: "colores vibrantes", "arte tipo acuarela", "estilo oscuro".
- **buscar_comics_por_autor**: cómics de un autor específico.
- **buscar_comics_por_genero**: filtrar por género o etiqueta concreta.
- **filtrar_comics_por_estado**: cómics en campaña, publicados, etc.
- **filtrar_comics_por_valoracion**: cómics mejor valorados.
- **filtrar_comics_por_meta**: por rango de meta de recaudación.
- **obtener_detalle_comic**: info completa de un cómic por título.

## Reglas
1. SIEMPRE usa alguna herramienta antes de responder. Nunca inventes cómics.
2. Si el usuario describe algo subjetivo ("algo triste", "con magia"), usa
   `buscar_comics_similares`.
3. Si describe estilo visual ("con mucho color", "dibujo realista"), usa
   `buscar_comics_por_estilo_visual`.
4. Si pide datos concretos (autor, género, estado), usa la herramienta específica.
5. Si el usuario pregunta por un cómic concreto por nombre, usa `obtener_detalle_comic`.
6. Puedes combinar herramientas si es necesario.
7. Responde en español, de forma concisa y amigable.
8. Si no encuentras nada, dilo claramente y sugiere alternativas.
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)


def get_agent_response(user_message: str) -> str:
    """Envía el mensaje al agente y retorna la respuesta final."""
    try:
        result = agent.invoke({
            "messages": [("user", user_message)]
        })
        return result["messages"][-1].content
    except Exception as e:
        print(f"Error en el agente IA: {e}")
        return "Lo siento, tuve un problema interno al buscar en el catálogo."