import os
import json
from huggingface_hub import InferenceClient

import requests

def get_embedding(text):
    token = os.getenv("HF_TOKEN")
    # Inicializamos el cliente oficial
    client = InferenceClient(token=token)
    
    try:
        # Usamos el modelo e5-base que genera exactamente 768 dimensiones
        # Y recordamos el prefijo "passage: " que requiere este modelo en particular
        resultado = client.feature_extraction(
            f"passage: {text}",
            model="intfloat/multilingual-e5-base"
        )
        
        # El cliente devuelve un numpy array (ej. de tamaño [1, 768])
        # Lo aplanamos (.flatten) y lo pasamos a lista nativa de Python (.tolist())
        # que es el formato exacto que pgvector necesita para guardar en la base de datos
        vector_lista = resultado.flatten().tolist()
        
        return vector_lista

    except Exception as e:
        print(f"Error generando vector con InferenceClient: {e}")
        return None