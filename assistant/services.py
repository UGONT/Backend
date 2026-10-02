import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from .tools import buscar_comics_similares

# 1. Inicializamos tu modelo Lite
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
)

# 2. Definimos la lista de herramientas disponibles
tools = [buscar_comics_similares]

# 3. Actualizamos el Prompt para soportar herramientas
system_prompt = """
Eres un asistente experto en cómics independientes. Tu objetivo es ayudar a los lectores a descubrir nuevas historias en nuestra plataforma.
SIEMPRE que te pregunten por cómics, usa la herramienta de búsqueda en la base de datos antes de responder. Nunca inventes títulos.
Responde de forma concisa y amigable.
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    # Este placeholder es obligatorio: es la "memoria de trabajo" donde 
    # el agente anota los resultados de las herramientas antes de responder.
    ("placeholder", "{agent_scratchpad}"), 
])

# 4. Creamos el agente y su ejecutor
agent = create_tool_calling_agent(llm, tools, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def get_agent_response(user_message: str) -> str:
    """Envía el mensaje al agente y retorna la respuesta final."""
    try:
        # AgentExecutor usa 'input' como variable por defecto
        respuesta = agent_executor.invoke({"input": user_message})
        return respuesta["output"]
    except Exception as e:
        print(f"Error en el agente IA: {e}")
        return "Lo siento, tuve un problema interno al buscar en el catálogo."




""" 
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Inicializamos el modelo (Flash es ideal para chat rápido y de bajo costo)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    # El token se carga automáticamente desde GOOGLE_API_KEY en el entorno
)

# Definimos el System Prompt (El "alma" de tu agente)
system_prompt = """
#Eres un asistente experto en cómics independientes. Tu objetivo es ayudar a los 
#lectores a descubrir nuevas historias, informar sobre campañas de crowdfunding 
#y recomendar títulos de nuestro catálogo. 
#Responde de forma concisa, amigable y con entusiasmo por el arte independiente.
"""

# Creamos la plantilla combinando el contexto del sistema con el mensaje del usuario
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{mensaje_usuario}")
])

# Creamos la cadena (Chain) de ejecución
agent_chain = prompt_template | llm

def get_agent_response(user_message: str) -> str:
    #Envía el mensaje a Gemini y retorna la respuesta en texto.
    try:
        respuesta = agent_chain.invoke({"mensaje_usuario": user_message})
        return respuesta.content
    except Exception as e:
        print(f"Error en el agente IA: {e}")
        return "Lo siento, tuve un problema de conexión con la red neuronal. ¿Puedes repetir?" 
"""