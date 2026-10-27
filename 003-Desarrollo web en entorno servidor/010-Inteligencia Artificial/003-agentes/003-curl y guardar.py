import time
import subprocess

while True:
    print("Yo soy un agente")

    subprocess.run([
        "curl",
        "-L",
        "-s",
        "https://www.aemet.es/xml/municipios/localidad_46250.xml",
        "-o",
        "aemet.xml"
    ])

    time.sleep(60)