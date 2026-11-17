import requests                                      # Importamos peticiones HTTP

ruta = "http://localhost:11434/api/generate"         # Dirección de Ollama
modelo = "codegemma:7b"                              # Modelo que utilizaremos
pregunta = "¿Qué es Python? Responde en un único párrafo"                         # Pregunta para la IA
flujo = False                                        # Desactivamos streaming

respuesta = requests.post(ruta, json={               # Enviamos petición POST
    "model": modelo,                                 # Indicamos el modelo
    "prompt": pregunta,                              # Enviamos la pregunta
    "stream": flujo                                  # Respuesta completa
}, timeout=120)                                      # Tiempo máximo de espera

respuesta.raise_for_status()                         # Comprobamos errores HTTP

print(respuesta.json()["response"])                  # Mostramos la respuesta