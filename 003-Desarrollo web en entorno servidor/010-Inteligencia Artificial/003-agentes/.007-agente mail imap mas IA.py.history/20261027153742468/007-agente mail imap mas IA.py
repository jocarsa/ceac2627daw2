
import os
import imaplib
import email
import json
import urllib.request
from email import policy

# Variables de entorno
servidor = os.environ["IMAP_SERVER"]
usuario = os.environ["IMAP_USER"]
password = os.environ["IMAP_PASSWORD"]

# Configuración Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "granite4.1:8b"


def analizar_correo(asunto, remitente, cuerpo):

    prompt = f"""
Eres un asistente especializado en gestionar prácticas
de Formación Profesional.

Analiza el siguiente correo electrónico.

Determina si una empresa, organización o persona
está solicitando alumnos para realizar prácticas
en su empresa.

Considera solicitudes de:
- Alumnos en prácticas
- Estudiantes de FP
- FCT
- Formación en empresa
- Formación dual
- Candidatos para prácticas

IMPORTANTE:
No confundas una oferta de prácticas con un correo
informativo, publicidad o una conversación genérica.

CORREO:
Remitente: {remitente}
Asunto: {asunto}
Contenido:
{cuerpo[:12000]}

Responde EXCLUSIVAMENTE con JSON válido:

{{
    "solicita_alumnos": false,
    "empresa": "",
    "motivo": ""
}}
"""

    datos = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0
        }
    }

    peticion = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(
        peticion,
        timeout=180
    ) as respuesta:

        resultado = json.loads(
            respuesta.read().decode("utf-8")
        )

    return json.loads(resultado["response"])


def obtener_cuerpo(mensaje):

    cuerpo = mensaje.get_body(
        preferencelist=("plain", "html")
    )

    if cuerpo:
        contenido = cuerpo.get_content()

        if isinstance(contenido, str):
            return contenido

    return "Sin contenido disponible"


# Conectar al servidor IMAP
conexion = imaplib.IMAP4_SSL(servidor, 993)
conexion.login(usuario, password)

try:
    estado, _ = conexion.select("INBOX", readonly=True)

    if estado != "OK":
        raise RuntimeError("No se pudo abrir INBOX")

    estado, datos = conexion.uid("search", None, "ALL")

    if estado == "OK":

        ultimos = datos[0].split()[-5:]
        encontrados = 0

        for uid in reversed(ultimos):

            estado, mensaje_datos = conexion.uid(
                "fetch", uid, "(BODY.PEEK[])"
            )

            if estado != "OK":
                continue

            partes = [
                parte[1]
                for parte in mensaje_datos
                if isinstance(parte, tuple)
                and isinstance(parte[1], bytes)
            ]

            if not partes:
                continue

            mensaje = email.message_from_bytes(
                partes[0],
                policy=policy.default
            )

            asunto = str(mensaje.get("Subject", ""))
            remitente = str(mensaje.get("From", ""))
            fecha = str(mensaje.get("Date", ""))

            cuerpo = obtener_cuerpo(mensaje)

            print("\n" + "-" * 60)
            print("Fecha:", fecha)
            print("De:", remitente)
            print("Asunto:", asunto)

            try:
                analisis = analizar_correo(
                    asunto,
                    remitente,
                    cuerpo
                )

                if analisis.get("solicita_alumnos") is True:

                    encontrados += 1

                    print("SOLICITA ALUMNOS: SÍ")
                    print(
                        "Empresa:",
                        analisis.get("empresa", "")
                    )
                    print(
                        "Motivo:",
                        analisis.get("motivo", "")
                    )

                else:
                    print("SOLICITA ALUMNOS: NO")

            except Exception as error:
                print("Error analizando correo:", error)

        print("\n" + "=" * 60)
        print("Correos analizados:", len(ultimos))
        print("Solicitudes detectadas:", encontrados)

finally:
    conexion.logout()
