import requests                                      # Importamos peticiones HTTP


ruta = "http://localhost:11434/api/generate"         # Dirección de Ollama

objetivo = """
	Dame el codigo PHP+HTML+CSS de una calculadora de IVA
  que tenga inputs, formulario, y procesamiento con PHP POST
  No quiero explicacion, no quiero fences, no quiero markdown
  quiero todo el código en un solo archivo PHP+HTML+CSS
  No me pongas fences markdown
  Crea un estilo bonito - pero crea un style dentro de HTML
  Es decir no me hagas diferentes archivo, hazmelo monolítico single-file
  
""" 																									# Pregunta para la IA
flujo = False                                        # Desactivamos streaming

############# AGENTE 1 ################################################
modelo = "codegemma:7b"                              # Modelo que utilizaremos
archivo = open("objetivo/index.php",'w')						# Abro un archivo para escribir
respuesta = requests.post(ruta, json={               # Enviamos petición POST
    "model": modelo,                                 # Indicamos el modelo
    "prompt": objetivo,                              # Enviamos la pregunta
    "stream": flujo                                  # Respuesta completa
}, timeout=120)                                      # Tiempo máximo de espera
respuesta.raise_for_status()                         # Comprobamos errores HTTP
respuestafinal = respuesta.json()["response"]        # Mostramos la respuesta
archivo.write(respuestafinal)
archivo.close()
############# AGENTE 1 ################################################

############# AGENTE 2 ################################################
modelo = "qwen2.5-coder:7b"                              # Modelo que utilizaremos
archivo = open("objetivo/index.php",'r')						# Abro un archivo para escribir
lineas = archivo.readlines()
contenido = ""
for linea in lineas:
  contenido += linea
  
respuesta = requests.post(ruta, json={               # Enviamos petición POST
    "model": modelo,                                 # Indicamos el modelo
    "prompt": """Comprueba si el arhivo: 
    """+contenido+""" 
    ha cumplido con el objetivo: 
    """+objetivo+""" """,                              # Enviamos la pregunta
    "stream": flujo                                  # Respuesta completa
}, timeout=120)                                      # Tiempo máximo de espera
respuesta.raise_for_status()                         # Comprobamos errores HTTP
respuestafinal = respuesta.json()["response"]        # Mostramos la respuesta
print(respuestafinal)
archivo.close()
############# AGENTE 2 ################################################



