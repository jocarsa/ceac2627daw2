
import requests
import json
import re
import ast
import subprocess
from pathlib import Path

# CONFIGURACIÓN ####################################################

RUTA = "http://localhost:11434/api/generate"

MODELO_GENERADOR = "codegemma:7b"
MODELO_EVALUADOR = "qwen2.5-coder:7b"

CARPETA = Path("objetivo")
TIMEOUT = 600

MAX_ARCHIVOS = 30
MAX_BYTES_ARCHIVO = 100_000
MAX_CARACTERES_EVALUACION = 100_000

# FUNCIONES ########################################################

def preguntar_ia(modelo, pregunta, formato=None):
    print(f"\nConsultando IA: {modelo}")

    datos = {
        "model": modelo,
        "prompt": pregunta,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 16384
        }
    }

    if formato:
        datos["format"] = formato

    respuesta = requests.post(
        RUTA,
        json=datos,
        timeout=TIMEOUT
    )

    respuesta.raise_for_status()

    return respuesta.json()["response"]


def extraer_json(texto):
    # Admitir una respuesta JSON con o sin fences
    texto = texto.strip()

    texto = re.sub(
        r"^```(?:json)?\s*",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(r"\s*```$", "", texto)

    return json.loads(texto)


def ruta_segura(nombre):
    # Evitar que la IA escriba fuera de objetivo/
    ruta = (CARPETA / nombre).resolve()
    raiz = CARPETA.resolve()

    if ruta == raiz or raiz not in ruta.parents:
        raise ValueError(f"Ruta no permitida: {nombre}")

    return ruta


def guardar_proyecto(proyecto):
    archivos = proyecto.get("archivos", [])

    if not isinstance(archivos, list):
        raise ValueError("El JSON no contiene archivos válidos")

    if not 1 <= len(archivos) <= MAX_ARCHIVOS:
        raise ValueError("Número de archivos no permitido")

    CARPETA.mkdir(parents=True, exist_ok=True)

    guardados = []

    for archivo in archivos:
        nombre = archivo["ruta"]
        contenido = archivo["contenido"]

        if not isinstance(contenido, str):
            raise ValueError(f"Contenido inválido: {nombre}")

        if len(contenido.encode("utf-8")) > MAX_BYTES_ARCHIVO:
            raise ValueError(f"Archivo demasiado grande: {nombre}")

        destino = ruta_segura(nombre)

        destino.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        destino.write_text(
            contenido,
            encoding="utf-8"
        )

        guardados.append(destino)

        print(f"  Creado: {destino}")

    return guardados


def comprobar_sintaxis(archivo):
    extension = archivo.suffix.lower()

    if extension == ".py":
        try:
            ast.parse(archivo.read_text(encoding="utf-8"))
            return "Sintaxis Python correcta"
        except SyntaxError as error:
            return f"Error Python: {error}"

    if extension == ".php":
        try:
            resultado = subprocess.run(
                ["php", "-l", str(archivo)],
                capture_output=True,
                text=True,
                timeout=15
            )
            return (
                resultado.stdout.strip()
                or resultado.stderr.strip()
            )
        except FileNotFoundError:
            return "PHP CLI no instalado"
        except subprocess.TimeoutExpired:
            return "Tiempo de comprobación agotado"

    if extension == ".json":
        try:
            json.loads(archivo.read_text(encoding="utf-8"))
            return "JSON válido"
        except json.JSONDecodeError as error:
            return f"Error JSON: {error}"

    return "Sin comprobación sintáctica automática"


def generar_informe_carpeta(archivos):
    partes = []

    partes.append("# INVENTARIO DEL PROYECTO\n")

    for archivo in archivos:
        relativo = archivo.relative_to(CARPETA)
        contenido = archivo.read_text(encoding="utf-8")

        partes.append(
            f"- {relativo} | "
            f"{len(contenido.splitlines())} líneas | "
            f"{archivo.stat().st_size} bytes"
        )

    partes.append("\n# CONTENIDO Y SINTAXIS\n")

    for archivo in archivos:
        relativo = archivo.relative_to(CARPETA)
        contenido = archivo.read_text(encoding="utf-8")

        partes.append(f"\n## ARCHIVO: {relativo}")
        partes.append(
            f"Comprobación: {comprobar_sintaxis(archivo)}"
        )
        partes.append("CONTENIDO:")
        partes.append(contenido)

    informe = "\n".join(partes)

    if len(informe) > MAX_CARACTERES_EVALUACION:
        informe = informe[:MAX_CARACTERES_EVALUACION]
        informe += (
            "\n\n[INFORME TRUNCADO: "
            "no se ha incluido todo el proyecto]"
        )

    return informe


# AGENTE 1: GENERADOR ##############################################

def agente_generador(objetivo):
    print("\n========== AGENTE 1: GENERADOR ==========")

    prompt = f"""
Eres un desarrollador senior especializado en aplicaciones CRUD.

OBJETIVO DEL USUARIO:
{objetivo}

Debes crear una aplicación CRUD completa.

REQUISITOS:
- Aplicación funcional en PHP 8 y SQLite.
- HTML, CSS y JavaScript.
- Interfaz moderna, profesional y responsive.
- Operaciones CREATE, READ, UPDATE y DELETE.
- Formularios para introducir y editar registros.
- Listado de registros.
- Búsqueda y filtrado.
- Validación en servidor.
- Consultas preparadas PDO.
- Protección frente a XSS.
- Base de datos SQLite inicializada automáticamente.
- Sin dependencias externas obligatorias.
- No utilizar frameworks.
- No incluir explicaciones fuera del JSON.

Devuelve exclusivamente un objeto JSON válido:

{{
  "nombre": "Nombre de la aplicación",
  "descripcion": "Descripción breve",
  "archivos": [
    {{
      "ruta": "index.php",
      "contenido": "Código completo del archivo"
    }},
    {{
      "ruta": "estilo.css",
      "contenido": "Código completo del archivo"
    }},
    {{
      "ruta": "app.js",
      "contenido": "Código completo del archivo"
    }}
  ]
}}

IMPORTANTE:
- El contenido debe ser código real, no pseudocódigo.
- No utilices marcadores TODO ni código incompleto.
- Escapa correctamente el contenido JSON.
- Todos los archivos deben ser coherentes entre sí.
- No uses rutas absolutas.
"""

    respuesta = preguntar_ia(
        MODELO_GENERADOR,
        prompt,
        formato="json"
    )

    proyecto = extraer_json(respuesta)

    archivos = guardar_proyecto(proyecto)

    return proyecto, archivos


# AGENTE 2: EVALUADOR ##############################################

def agente_evaluador(objetivo, archivos):
    print("\n========== AGENTE 2: EVALUADOR ==========")

    informe_carpeta = generar_informe_carpeta(archivos)

    # Guardamos la evidencia entregada al evaluador
    (CARPETA / "informe_contenido.md").write_text(
        informe_carpeta,
        encoding="utf-8"
    )

    prompt = f"""
Eres un auditor senior de software.

Tu trabajo consiste en evaluar una aplicación generada
por otra inteligencia artificial.

OBJETIVO ORIGINAL:
{objetivo}

INVENTARIO, CÓDIGO Y COMPROBACIONES:
{informe_carpeta}

INSTRUCCIONES:

1. Comprueba si se cumple el objetivo original.
2. Evalúa CREATE, READ, UPDATE y DELETE por separado.
3. Comprueba la estructura de archivos.
4. Analiza la calidad del código.
5. Detecta errores de lógica.
6. Detecta problemas de seguridad.
7. Analiza la interfaz y su diseño.
8. Comprueba coherencia entre archivos.
9. Identifica funcionalidades incompletas.
10. Propón mejoras concretas.

No ejecutes ni presupongas pruebas que no consten
en el informe. Diferencia claramente:
- Funcionalidad observada en el código.
- Funcionalidad comprobada mediante herramientas.
- Funcionalidad no verificada.

Devuelve un informe Markdown con:

# INFORME DE EVALUACIÓN

## 1. Resumen ejecutivo
## 2. Cumplimiento del objetivo
## 3. Evaluación del CRUD
## 4. Calidad del código
## 5. Seguridad
## 6. Diseño e interfaz
## 7. Errores detectados
## 8. Mejoras recomendadas
## 9. Puntuación final (0-100)
## 10. Veredicto: APROBADO o SUSPENDIDO

Sé exigente y justifica las conclusiones.

No generes código nuevo.
No modifiques ningún archivo.
"""

    evaluacion = preguntar_ia(
        MODELO_EVALUADOR,
        prompt
    )

    destino = CARPETA / "informe_evaluacion.md"

    destino.write_text(
        evaluacion,
        encoding="utf-8"
    )

    print(f"\nInforme guardado en: {destino}")

    return evaluacion


# PROGRAMA PRINCIPAL ###############################################

def main():
    print("=" * 60)
    print("JOCARSA | GENERADOR Y EVALUADOR DE CRUD")
    print("=" * 60)

    objetivo = input(
        "\n¿Qué aplicación CRUD quieres crear?\n> "
    ).strip()

    if not objetivo:
        print("No has indicado ningún objetivo.")
        return

    # Guardar requisitos originales
    CARPETA.mkdir(parents=True, exist_ok=True)

    (CARPETA / "objetivo.txt").write_text(
        objetivo,
        encoding="utf-8"
    )

    # Primera y única generación
    proyecto, archivos = agente_generador(objetivo)

    print("\nAplicación generada:")
    print(proyecto.get("nombre", "Sin nombre"))

    # Primera y única evaluación
    evaluacion = agente_evaluador(objetivo, archivos)

    print("\n========== RESULTADO ==========\n")
    print(evaluacion)

    print("\nProceso finalizado.")
    print("No se realizarán nuevas iteraciones.")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as error:
        print(f"\nError de comunicación con Ollama: {error}")
    except (ValueError, KeyError, TypeError) as error:
        print(f"\nError procesando el proyecto: {error}")
