import os
import imaplib
import email
from email import policy
from email.header import decode_header

# Variables de entorno
servidor = os.environ["IMAP_SERVER"]
usuario = os.environ["IMAP_USER"]
password = os.environ["IMAP_PASSWORD"]

# Conectar al servidor IMAP
conexion = imaplib.IMAP4_SSL(servidor, 993)
conexion.login(usuario, password)

# Seleccionar bandeja de entrada
conexion.select("INBOX", readonly=True)

# Buscar todos los mensajes
estado, datos = conexion.uid("search", None, "ALL")

if estado == "OK":
    ultimos = datos[0].split()[-5:]

    for uid in reversed(ultimos):
        estado, mensaje_datos = conexion.uid(
            "fetch", uid, "(BODY.PEEK[])"
        )

        if estado != "OK":
            continue

        # Crear objeto EmailMessage
        mensaje = email.message_from_bytes(
            mensaje_datos[0][1],
            policy=policy.default
        )

        # Decodificar asunto
        asunto = str(mensaje.get("Subject", ""))

        print("Fecha:", mensaje.get("Date"))
        print("De:", mensaje.get("From"))
        print("Asunto:", asunto)

        # Obtener cuerpo en texto plano
        cuerpo = mensaje.get_body(preferencelist=("plain",))

        if cuerpo:
            print("Cuerpo:", cuerpo.get_content())
        else:
            print("Cuerpo: No disponible en texto plano")

        print("-" * 60)

conexion.logout()