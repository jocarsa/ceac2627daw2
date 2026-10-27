import time
import subprocess

while True:
    print("Yo soy un agente")

    # Descargar XML de AEMET
    subprocess.run([
        "curl",
        "-L",
        "-s",
        "https://www.aemet.es/xml/municipios/localidad_46250.xml",
        "-o",
        "aemet.xml"
    ], check=True)

    # Leer el XML
    with open("aemet.xml", "r", encoding="utf-8") as archivo:
        xml = archivo.read()

    # Crear el prompt
    prompt = f"""
    Eres un agente meteorológico.

    Interpreta el siguiente XML de AEMET.

    Explica en español:
    - La previsión del tiempo.
    - Las temperaturas máximas y mínimas.
    - La probabilidad de lluvia.
    - El viento.
    - Recomendaciones para el día.

    Utiliza exclusivamente los datos del XML.
    Si algún dato no está disponible, indícalo.

    XML:
    {xml}
    """

    # Ejecutar Ollama
    resultado = subprocess.run(
        ["ollama", "run", "granite4.1:8b"],
        input=prompt,
        text=True,
        capture_output=True
    )

    # Mostrar respuesta
    if resultado.returncode == 0:
        print("\n--- INTERPRETACIÓN DE OLLAMA ---\n")
        print(resultado.stdout)
    else:
        print("Error de Ollama:", resultado.stderr)

    # Esperar 60 segundos
    time.sleep(60)