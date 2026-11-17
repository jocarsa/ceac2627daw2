
import os
import imaplib
import email
import json
import urllib.request

from email import policy
from email.utils import parseaddr, parsedate_to_datetime
from html.parser import HTMLParser


# ============================================
# CONFIGURACIÓN
# ============================================

servidor = os.environ["IMAP_SERVER"]
usuario = os.environ["IMAP_USER"]
password = os.environ["IMAP_PASSWORD"]

API_URL = "https://notificaciones.jocarsa.com/api.php"
API_USUARIO = "jocarsa"
API_PASSWORD = os.environ.get("NOTIFICACIONES_PASSWORD", "jocarsa")
AGENTE_CLAVE = "practicas-damdaw"
AGENTE_NOMBRE = "Prácticas DAMDAW"
REGISTRO_ENVIADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notificaciones_enviadas.json")

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
# AUTENTICACIÓN Y ENVÍO A API V3
# ============================================

def api_post(datos, token=None):
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["X-Session-Token"] = token
    peticion = urllib.request.Request(
        API_URL,
        data=json.dumps(datos, ensure_ascii=False).encode("utf-8"),
        headers=cabeceras,
        method="POST"
    )
    try:
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            resultado = json.load(respuesta)
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"API HTTP {error.code}: {detalle}") from error
    if not resultado.get("ok"):
        raise RuntimeError(f"API: {resultado.get('error', 'Error desconocido')}")
    return resultado


def iniciar_sesion_api():
    resultado = api_post({
        "accion": "login",
        "usuario": API_USUARIO,
        "password": API_PASSWORD
    })
    return resultado["token"]


def leer_enviados():
    try:
        with open(REGISTRO_ENVIADOS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return set(datos) if isinstance(datos, list) else set()
    except FileNotFoundError:
        return set()


def guardar_enviados(enviados):
    temporal = REGISTRO_ENVIADOS + ".tmp"
    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump(sorted(enviados), archivo, ensure_ascii=False, indent=2)
    os.replace(temporal, REGISTRO_ENVIADOS)


def enviar_notificacion(solicitud, token):
    empresa = solicitud.get("empresa", "Empresa")
    titulo = f"Prácticas FP · {empresa}"[:160]
    campos = [
        ("Fecha correo", "fecha_correo"),
        ("Asunto", "asunto"),
        ("Remitente", "remitente"),
        ("Contacto", "persona_contacto"),
        ("Cargo", "cargo"),
        ("Email", "email_contacto"),
        ("Teléfono", "telefono"),
        ("Dirección", "direccion"),
        ("Localidad", "localidad"),
        ("Provincia", "provincia"),
        ("Especialidad", "especialidad"),
        ("Alumnos", "numero_alumnos"),
        ("Modalidad", "modalidad_practicas"),
        ("Inicio", "fecha_inicio"),
        ("Duración", "duracion"),
        ("Horario", "horario"),
        ("Remuneración", "remuneracion"),
        ("Resumen", "resumen"),
        ("Observaciones", "observaciones"),
    ]
    descripcion = "\n".join(
        f"{etiqueta}: {str(solicitud.get(clave) or '').strip()}"
        for etiqueta, clave in campos
        if str(solicitud.get(clave) or "").strip()
    )[:4000]
    return api_post({
        "accion": "enviar",
        "agente": AGENTE_CLAVE,
        "agente_nombre": AGENTE_NOMBRE,
        "titulo": titulo,
        "descripcion": descripcion or "Nueva solicitud de alumnos en prácticas.",
        "icono": "🎓"
    }, token)


# ============================================
# PROGRAMA PRINCIPAL
# ============================================

def main():

    empresas = {}
    enviados = leer_enviados()
    token_api = iniciar_sesion_api()
    nuevas = 0

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

                # Evitar reenvíos en ejecuciones posteriores.
                # El UID se identifica junto con servidor y buzón IMAP.
                identificador = f"{servidor}|{usuario}|INBOX|{uid.decode()}"
                if identificador in enviados:
                    continue

                respuesta = enviar_notificacion(analisis, token_api)
                enviados.add(identificador)
                guardar_enviados(enviados)
                nuevas += 1
                print(f"Notificación enviada: {empresa} (ID {respuesta.get('id')})", flush=True)

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

    print("Notificaciones nuevas enviadas:", nuevas)


if __name__ == "__main__":
    main()
