
import os
import imaplib
import email
import json
import urllib.request
import smtplib
import ssl
import html

from email import policy
from email.utils import parseaddr, parsedate_to_datetime
from email.message import EmailMessage
from html.parser import HTMLParser


# ============================================
# CONFIGURACIÓN
# ============================================

servidor = os.environ["IMAP_SERVER"]
usuario = os.environ["IMAP_USER"]
password = os.environ["IMAP_PASSWORD"]

smtp_servidor = os.environ["SMTP_SERVER"]
smtp_puerto = int(os.environ.get("SMTP_PORT", "587"))

destinatario_informe = "info@josevicentecarratala.com"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "granite4.1:8b"

LIMITE_CORREOS = 50


# ============================================
# EXTRAER TEXTO DE HTML
# ============================================

class ExtractorHTML(HTMLParser):

    def __init__(self):
        super().__init__()
        self.textos = []

    def handle_data(self, data):
        if data.strip():
            self.textos.append(data.strip())

    def obtener_texto(self):
        return " ".join(self.textos)


def limpiar_html(contenido):
    extractor = ExtractorHTML()
    extractor.feed(contenido)
    return extractor.obtener_texto()


# ============================================
# OBTENER CUERPO DEL CORREO
# ============================================

def obtener_cuerpo(mensaje):

    parte = mensaje.get_body(
        preferencelist=("plain", "html")
    )

    if parte is None:
        return ""

    contenido = parte.get_content()

    if not isinstance(contenido, str):
        return ""

    if parte.get_content_type() == "text/html":
        return limpiar_html(contenido)

    return contenido


# ============================================
# ANALIZAR CORREO CON OLLAMA
# ============================================

def analizar_correo(asunto, remitente, cuerpo):

    prompt = f"""
Eres un asistente especializado en gestionar
prácticas de Formación Profesional.

Analiza el siguiente correo electrónico.

Determina si una empresa está solicitando
alumnos para realizar prácticas.

Incluye solicitudes de:
- FCT
- Formación dual
- Formación en empresa
- Alumnos de FP
- Estudiantes en prácticas
- Candidatos para prácticas

IMPORTANTE:

Solo marca solicita_alumnos como true cuando
exista una solicitud real de estudiantes
por parte de una empresa.

No incluyas:
- Publicidad
- Correos informativos
- Conversaciones genéricas
- Ofertas de empleo ordinarias
- Correos que únicamente mencionan prácticas

Si detectas una solicitud, extrae toda
la información disponible.

No inventes datos.

Si no conoces algún dato, utiliza
una cadena vacía.

El resumen debe explicar claramente qué
solicita la empresa, en 2-4 frases.

CORREO:

Remitente: {remitente}
Asunto: {asunto}

Contenido:
{cuerpo[:12000]}

Responde EXCLUSIVAMENTE con JSON válido:

{{
    "solicita_alumnos": false,
    "empresa": "",
    "persona_contacto": "",
    "cargo": "",
    "email_contacto": "",
    "telefono": "",
    "direccion": "",
    "localidad": "",
    "provincia": "",
    "especialidad": "",
    "numero_alumnos": "",
    "modalidad_practicas": "",
    "fecha_inicio": "",
    "duracion": "",
    "horario": "",
    "remuneracion": "",
    "resumen": "",
    "observaciones": ""
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
        headers={
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(
        peticion,
        timeout=180
    ) as respuesta:

        resultado = json.loads(
            respuesta.read().decode("utf-8")
        )

    return json.loads(resultado["response"])


# ============================================
# OBTENER FECHA
# ============================================

def obtener_fecha(mensaje):

    fecha_original = str(
        mensaje.get("Date", "")
    )

    try:
        fecha = parsedate_to_datetime(
            fecha_original
        )

        return fecha.strftime(
            "%d/%m/%Y %H:%M"
        )

    except Exception:
        return fecha_original


# ============================================
# CREAR INFORME HTML
# ============================================

def crear_informe(empresas):

    def escapar(valor):
        return html.escape(str(valor or ""))

    def fila(etiqueta, valor):

        if valor is None or str(valor).strip() == "":
            return ""

        return f"""
        <tr>
            <th>{escapar(etiqueta)}</th>
            <td>{escapar(valor)}</td>
        </tr>
        """

    total_solicitudes = sum(
        len(solicitudes)
        for solicitudes in empresas.values()
    )

    contenido = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f3f5fa;
                color: #263044;
                padding: 30px;
                line-height: 1.6;
            }}

            .contenedor {{
                max-width: 900px;
                margin: auto;
                background: white;
                padding: 35px;
                border-radius: 12px;
            }}

            h1 {{
                color: #4f5d95;
                margin-bottom: 5px;
            }}

            h2 {{
                color: #4f5d95;
                margin-top: 35px;
            }}

            h3 {{
                color: #35446e;
            }}

            .resumen {{
                background: #eef1fa;
                padding: 18px;
                border-radius: 8px;
                margin: 20px 0;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 25px;
            }}

            th, td {{
                padding: 10px 12px;
                border-bottom: 1px solid #e5e8ef;
                text-align: left;
                vertical-align: top;
            }}

            th {{
                width: 190px;
                color: #4f5d95;
                background: #f8f9fc;
            }}

            .empresa {{
                border-top: 4px solid #e88b2f;
                padding-top: 15px;
                margin-top: 35px;
            }}

            .pie {{
                margin-top: 35px;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>

    <body>
    <div class="contenedor">

        <h1>JOCARSA | Prácticas</h1>

        <p>
            Informe automático de empresas
            interesadas en alumnos de Formación Profesional.
        </p>

        <div class="resumen">
            <strong>Empresas detectadas:</strong>
            {len(empresas)}
            <br>
            <strong>Solicitudes encontradas:</strong>
            {total_solicitudes}
        </div>
    """

    if not empresas:
        contenido += """
        <p>
            No se han detectado solicitudes de
            alumnos en los correos analizados.
        </p>
        """

    for indice, (clave, solicitudes) in enumerate(
        empresas.items(),
        start=1
    ):

        nombre_empresa = solicitudes[0]["empresa"]

        contenido += f"""
        <div class="empresa">

            <h2>
                {indice}.
                {escapar(nombre_empresa)}
            </h2>

            <p>
                Solicitudes detectadas:
                <strong>{len(solicitudes)}</strong>
            </p>
        """

        for numero, solicitud in enumerate(
            solicitudes,
            start=1
        ):

            contenido += f"""
            <h3>Solicitud {numero}</h3>

            <table>
            """

            campos = [
                ("Fecha del correo", "fecha_correo"),
                ("Asunto", "asunto"),
                ("Remitente original", "remitente"),
                ("Email remitente", "email_remitente"),
                ("Persona de contacto", "persona_contacto"),
                ("Cargo", "cargo"),
                ("Email de contacto", "email_contacto"),
                ("Teléfono", "telefono"),
                ("Dirección", "direccion"),
                ("Localidad", "localidad"),
                ("Provincia", "provincia"),
                ("Especialidad", "especialidad"),
                ("Número de alumnos", "numero_alumnos"),
                ("Modalidad", "modalidad_practicas"),
                ("Fecha de inicio", "fecha_inicio"),
                ("Duración", "duracion"),
                ("Horario", "horario"),
                ("Remuneración", "remuneracion"),
                ("Resumen", "resumen"),
                ("Observaciones", "observaciones")
            ]

            for etiqueta, campo in campos:
                contenido += fila(
                    etiqueta,
                    solicitud.get(campo, "")
                )

            contenido += """
            </table>
            """

        contenido += """
        </div>
        """

    contenido += """
        <div class="pie">
            Informe generado automáticamente
            mediante análisis de correo IMAP
            e inteligencia artificial local Ollama.
            Los datos extraídos deben verificarse
            antes de contactar con las empresas.
        </div>

    </div>
    </body>
    </html>
    """

    return contenido


# ============================================
# ENVIAR INFORME POR SMTP
# ============================================

def enviar_informe(empresas):

    informe_html = crear_informe(empresas)

    total_solicitudes = sum(
        len(solicitudes)
        for solicitudes in empresas.values()
    )

    mensaje = EmailMessage()

    mensaje["From"] = usuario
    mensaje["To"] = destinatario_informe

    mensaje["Subject"] = (
        "JOCARSA | Solicitudes de alumnos en prácticas "
        f"({len(empresas)} empresas)"
    )

    texto = (
        "Informe automático de solicitudes de prácticas.\n\n"
        f"Empresas detectadas: {len(empresas)}\n"
        f"Solicitudes detectadas: {total_solicitudes}\n\n"
        "Consulta la versión HTML para ver los detalles."
    )

    mensaje.set_content(texto)

    mensaje.add_alternative(
        informe_html,
        subtype="html"
    )

    contexto = ssl.create_default_context()

    if smtp_puerto == 465:

        with smtplib.SMTP_SSL(
            smtp_servidor,
            smtp_puerto,
            context=contexto,
            timeout=60
        ) as smtp:

            smtp.login(usuario, password)
            smtp.send_message(mensaje)

    else:

        with smtplib.SMTP(
            smtp_servidor,
            smtp_puerto,
            timeout=60
        ) as smtp:

            smtp.ehlo()
            smtp.starttls(context=contexto)
            smtp.ehlo()

            smtp.login(usuario, password)
            smtp.send_message(mensaje)

    print(
        "\nInforme enviado a:",
        destinatario_informe
    )


# ============================================
# PROGRAMA PRINCIPAL
# ============================================

def main():

    empresas = {}

    conexion = imaplib.IMAP4_SSL(
        servidor,
        993
    )

    try:

        conexion.login(usuario, password)

        estado, _ = conexion.select(
            "INBOX",
            readonly=True
        )

        if estado != "OK":
            raise RuntimeError(
                "No se pudo abrir INBOX"
            )

        estado, datos = conexion.uid(
            "search",
            None,
            "ALL"
        )

        if estado != "OK":
            raise RuntimeError(
                "No se pudieron buscar correos"
            )

        ultimos = datos[0].split()[
            -LIMITE_CORREOS:
        ]

        for uid in reversed(ultimos):

            try:

                estado, mensaje_datos = conexion.uid(
                    "fetch",
                    uid,
                    "(BODY.PEEK[])"
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

                asunto = str(
                    mensaje.get("Subject", "")
                )

                remitente = str(
                    mensaje.get("From", "")
                )

                nombre_remitente, email_remitente = (
                    parseaddr(remitente)
                )

                fecha = obtener_fecha(mensaje)

                cuerpo = obtener_cuerpo(mensaje)

                analisis = analizar_correo(
                    asunto,
                    remitente,
                    cuerpo
                )

                if analisis.get(
                    "solicita_alumnos"
                ) is not True:
                    continue

                empresa = str(
                    analisis.get("empresa", "")
                ).strip()

                if not empresa:
                    continue

                clave = empresa.casefold()

                # Incorporar metadatos reales del correo
                analisis["empresa"] = empresa
                analisis["fecha_correo"] = fecha
                analisis["asunto"] = asunto
                analisis["remitente"] = remitente
                analisis["email_remitente"] = (
                    email_remitente
                )

                # Fallback para persona de contacto
                if not analisis.get(
                    "persona_contacto"
                ):
                    analisis["persona_contacto"] = (
                        nombre_remitente
                    )

                # Fallback para email de contacto
                if not analisis.get(
                    "email_contacto"
                ):
                    analisis["email_contacto"] = (
                        email_remitente
                    )

                # Agrupar por empresa
                if clave not in empresas:
                    empresas[clave] = []

                    print(
                        "Empresa detectada:",
                        empresa,
                        flush=True
                    )

                # Evitar duplicados por UID
                if not any(
                    s.get("uid") == uid.decode()
                    for s in empresas[clave]
                ):

                    analisis["uid"] = uid.decode()

                    empresas[clave].append(
                        analisis
                    )

            except Exception as error:

                print(
                    "Error analizando UID",
                    uid.decode(),
                    ":",
                    error
                )

    finally:

        try:
            conexion.logout()
        except Exception:
            pass

    print(
        "\nTotal empresas:",
        len(empresas)
    )

    print(
        "Total solicitudes:",
        sum(
            len(solicitudes)
            for solicitudes in empresas.values()
        )
    )

    # Enviar un único informe al finalizar
    enviar_informe(empresas)


if __name__ == "__main__":
    main()
