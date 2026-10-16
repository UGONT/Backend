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
    make_recomendar_para_mi,
)

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7)

system_prompt = """
Eres un asistente experto en cómics independientes que ayuda a los lectores
a descubrir nuevas historias en nuestra plataforma de crowdfunding.

## Herramientas disponibles
- **buscar_comics_similares**: búsqueda semántica por temática/historia.
- **buscar_comics_por_estilo_visual**: búsqueda por estilo artístico de portada.
- **buscar_comics_por_autor**: cómics de un autor específico.
- **buscar_comics_por_genero**: filtrar por género o etiqueta.
- **filtrar_comics_por_estado**: cómics en campaña, publicados, etc.
- **filtrar_comics_por_valoracion**: mejor valorados.
- **filtrar_comics_por_meta**: por rango de meta.
- **obtener_detalle_comic**: info completa por título.
- **recomendar_para_mi**: recomendación personalizada basada en los gustos y
  cómics leídos del usuario actual. Úsala cuando el usuario diga "recomiéndame
  algo", "algo para mí", "qué me puede gustar".

## Reglas
1. SIEMPRE usa herramientas antes de responder. Nunca inventes cómics.
2. Si el usuario pide algo subjetivo ("algo triste", "con magia"), usa
   `buscar_comics_similares`.
3. Si pide estilo visual, usa `buscar_comics_por_estilo_visual`.
4. Si pide recomendaciones personalizadas, usa `recomendar_para_mi`.
5. Si pide datos concretos (autor, género, estado), usa la tool específica.
6. Si pregunta por un cómic concreto por nombre, usa `obtener_detalle_comic`.
7. Responde en español, conciso y amigable.
"""


def get_agent_response(user_message: str, user_id: int | None = None) -> str:
    """Envía el mensaje al agente y retorna la respuesta final."""
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
    
    # Añadimos el tool personalizado solo si hay usuario logueado
    if user_id:
        tools.append(make_recomendar_para_mi(user_id))
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )
    
    try:
        result = agent.invoke({"messages": [("user", user_message)]})
        return result["messages"][-1].content
    except Exception as e:
        print(f"Error en el agente IA: {e}")
        return "Lo siento, tuve un problema interno al buscar en el catálogo."