
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

Analiza este correo y determina si una empresa
está solicitando alumnos para realizar prácticas.

Incluye:
- FCT
- Formación dual
- Formación en empresa
- Alumnos de FP
- Estudiantes en prácticas
- Solicitudes de candidatos para prácticas

IMPORTANTE:
Solo responde true cuando exista una solicitud real
de alumnos por parte de una empresa.

No incluyas publicidad, correos informativos,
conversaciones genéricas ni ofertas de empleo ordinarias.

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

    return ""


# Conectar a IMAP
conexion = imaplib.IMAP4_SSL(servidor, 993)
conexion.login(usuario, password)

empresas = {}

try:
    estado, _ = conexion.select("INBOX", readonly=True)

    if estado != "OK":
        raise RuntimeError("No se pudo abrir INBOX")

    estado, datos = conexion.uid("search", None, "ALL")

    if estado != "OK":
        raise RuntimeError("No se pudieron buscar correos")

    # Últimos 50 correos
    ultimos = datos[0].split()[-50:]

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
        cuerpo = obtener_cuerpo(mensaje)

        try:
            analisis = analizar_correo(
                asunto,
                remitente,
                cuerpo
            )

            if analisis.get("solicita_alumnos") is True:

                empresa = str(
                    analisis.get("empresa", "")
                ).strip()

                if not empresa:
                    continue

                clave = empresa.casefold()

                if clave not in empresas:
                    empresas[clave] = empresa
                    print(empresa, flush=True)

        except Exception:
            continue

finally:
    conexion.logout()

print("\nTotal empresas:", len(empresas))
