import requests                                      # Importamos peticiones HTTP
archivo = open("objetivo/index.php",'w')							# Abro un archivo para escribir

ruta = "http://localhost:11434/api/generate"         # Dirección de Ollama
modelo = "codegemma:7b"                              # Modelo que utilizaremos
pregunta = """
	Dame el codigo PHP+HTML+CSS de una calculadora de IVA
  que tenga inputs, formulario, y procesamiento con PHP POST
  No quiero explicacion, no quiero fences, no quiero markdown
  Solo quiero el código PHP puro
""" 																									# Pregunta para la IA
flujo = False                                        # Desactivamos streaming

respuesta = requests.post(ruta, json={               # Enviamos petición POST
    "model": modelo,                                 # Indicamos el modelo
    "prompt": pregunta,                              # Enviamos la pregunta
    "stream": flujo                                  # Respuesta completa
}, timeout=120)                                      # Tiempo máximo de espera

respuesta.raise_for_status()                         # Comprobamos errores HTTP

respuestafinal = respuesta.json()["response"]        # Mostramos la respuesta
archivo.write(respuestafinal)

archivo.close()