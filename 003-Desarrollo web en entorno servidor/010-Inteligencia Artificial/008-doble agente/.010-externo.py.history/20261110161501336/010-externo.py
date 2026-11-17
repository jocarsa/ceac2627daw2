import requests
import os
import json
import re
import ast
import subprocess
from pathlib import Path

# CONFIGURACIÓN ####################################################

RUTA = "https://ages-friend-follow-jeremy.trycloudflare.com/daw/"  # API externa
TOKEN = os.getenv("JOCARSA_DAW_API_TOKEN", "jocarsa_phi4_2026_ClaveSegura_8f3a91b7")

MODELO_GENERADOR = "gpt-oss:20b"                    # IA que genera el CRUD
MODELO_EVALUADOR = "gpt-oss:20b"                # IA que evalúa el CRUD

DIRECTORIO = Path(__file__).resolve().parent         # Directorio del script
CARPETA = DIRECTORIO / "objetivo"                     # Carpeta de salida absoluta

TIMEOUT = 650                                        # Tiempo máximo de respuesta
MAX_ARCHIVOS = 30                                    # Máximo de archivos generados
MAX_BYTES_ARCHIVO = 100_000                          # Tamaño máximo por archivo
MAX_CARACTERES_EVALUACION = 100_000                  # Máximo de caracteres del informe

ARCHIVOS_INTERNOS = {                                # Archivos que no evaluamos
    "objetivo.txt",
    "informe_contenido.md",
    "informe_evaluacion.md"
}


# FUNCIONES GENERALES ##############################################

def preguntar_ia(modelo, pregunta, formato=None):
    print(f"\nConsultando API externa: {modelo}")

    # La API /daw/ utiliza nombres de campos en español.
    # No enviamos 'format' ni 'options', pues no forman parte
    # del contrato HTTP indicado. El formato se pide en el prompt.
    if formato == "json":
        pregunta += "\n\nResponde SOLO con JSON válido, sin Markdown."

    datos = {
        "token": TOKEN,
        "modelo": modelo,
        "mensaje": pregunta,
        "stream": False
    }

    respuesta = requests.post(
        RUTA,
        headers={"Content-Type": "application/json"},
        json=datos,
        timeout=(15, TIMEOUT)
    )
    respuesta.raise_for_status()

    try:
        resultado = respuesta.json()
    except ValueError as error:
        raise ValueError(
            f"La API no devolvió JSON HTTP válido: {respuesta.text[:500]}"
        ) from error

    if isinstance(resultado, str):
        return resultado
    if not isinstance(resultado, dict):
        raise ValueError(f"Respuesta inesperada de la API: {str(resultado)[:500]}")
    if resultado.get("error"):
        raise ValueError(f"Error de la API: {resultado['error']}")

    # Admitir envoltorios frecuentes sin asumir que todos existen.
    for clave in ("response", "respuesta", "resultado", "texto", "content", "mensaje"):
        valor = resultado.get(clave)
        if isinstance(valor, str):
            return valor
        if isinstance(valor, dict):
            for subclave in ("response", "respuesta", "content", "texto"):
                if isinstance(valor.get(subclave), str):
                    return valor[subclave]

    # Algunos endpoints devuelven directamente el objeto generado.
    if formato == "json" and isinstance(resultado.get("archivos"), list):
        return json.dumps(resultado, ensure_ascii=False)

    raise ValueError(
        "No se encontró el texto generado en la respuesta: "
        + json.dumps(resultado, ensure_ascii=False)[:700]
    )


def extraer_json(texto):
    texto = texto.strip()

    texto = re.sub(
        r"^```(?:json)?\s*",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r"\s*```$",
        "",
        texto
    )

    return json.loads(texto)


def ruta_segura(nombre):
    raiz = CARPETA.resolve()
    destino = (raiz / nombre).resolve()

    if destino == raiz or raiz not in destino.parents:
        raise ValueError(
            f"Ruta no permitida: {nombre}"
        )

    return destino


def guardar_proyecto(proyecto):
    archivos = proyecto.get("archivos", [])

    if not isinstance(archivos, list):
        raise ValueError(
            "El proyecto no contiene una lista de archivos"
        )

    if not 1 <= len(archivos) <= MAX_ARCHIVOS:
        raise ValueError(
            "Número de archivos no permitido"
        )

    CARPETA.mkdir(
        parents=True,
        exist_ok=True
    )

    guardados = []

    for archivo in archivos:
        nombre = archivo["ruta"]
        contenido = archivo["contenido"]

        if not isinstance(contenido, str):
            raise ValueError(
                f"Contenido inválido: {nombre}"
            )

        if len(contenido.encode("utf-8")) > MAX_BYTES_ARCHIVO:
            raise ValueError(
                f"Archivo demasiado grande: {nombre}"
            )

        destino = ruta_segura(nombre)

        if destino.name in ARCHIVOS_INTERNOS:
            raise ValueError(
                f"Nombre reservado: {nombre}"
            )

        destino.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        destino.write_text(
            contenido,
            encoding="utf-8"
        )

        guardados.append(destino)

        print(
            f"  Creado: {destino.relative_to(CARPETA)}"
        )

    return guardados


def obtener_archivos_proyecto():
    archivos = []

    if not CARPETA.exists():
        return archivos

    for archivo in sorted(CARPETA.rglob("*")):
        if not archivo.is_file():
            continue

        if archivo.name in ARCHIVOS_INTERNOS:
            continue

        if archivo.is_symlink():
            continue

        archivos.append(archivo.resolve())

    return archivos


# COMPROBACIÓN DE SINTAXIS #########################################

def comprobar_sintaxis(archivo):
    extension = archivo.suffix.lower()

    if extension == ".py":
        try:
            contenido = archivo.read_text(
                encoding="utf-8"
            )

            ast.parse(contenido)

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

            salida = (
                resultado.stdout.strip()
                or resultado.stderr.strip()
            )

            return salida

        except FileNotFoundError:
            return "PHP CLI no instalado"

        except subprocess.TimeoutExpired:
            return "Tiempo de comprobación agotado"

    if extension == ".json":
        try:
            contenido = archivo.read_text(
                encoding="utf-8"
            )

            json.loads(contenido)

            return "JSON válido"

        except json.JSONDecodeError as error:
            return f"Error JSON: {error}"

    return "Sin comprobación sintáctica automática"


# INFORME DE CONTENIDO #############################################

def generar_informe_carpeta(archivos):
    partes = []

    partes.append("# INVENTARIO DEL PROYECTO\n")

    total_lineas = 0
    total_bytes = 0

    for archivo in archivos:
        relativo = archivo.relative_to(CARPETA)

        contenido = archivo.read_text(
            encoding="utf-8",
            errors="replace"
        )

        lineas = len(contenido.splitlines())
        bytes_archivo = archivo.stat().st_size

        total_lineas += lineas
        total_bytes += bytes_archivo

        partes.append(
            f"- {relativo} | "
            f"{lineas} líneas | "
            f"{bytes_archivo} bytes"
        )

    partes.append("\n# ESTADÍSTICAS GENERALES\n")

    partes.append(
        f"- Número de archivos: {len(archivos)}"
    )

    partes.append(
        f"- Total de líneas: {total_lineas}"
    )

    partes.append(
        f"- Tamaño total: {total_bytes} bytes"
    )

    partes.append("\n# CONTENIDO Y SINTAXIS\n")

    for archivo in archivos:
        relativo = archivo.relative_to(CARPETA)

        contenido = archivo.read_text(
            encoding="utf-8",
            errors="replace"
        )

        sintaxis = comprobar_sintaxis(archivo)

        partes.append(
            f"\n## ARCHIVO: {relativo}"
        )

        partes.append(
            f"Comprobación: {sintaxis}"
        )

        partes.append("\nCONTENIDO:\n")

        partes.append(contenido)

    informe = "\n".join(partes)

    if len(informe) > MAX_CARACTERES_EVALUACION:
        informe = (
            informe[:MAX_CARACTERES_EVALUACION]
            + "\n\n[INFORME TRUNCADO]"
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
- Validación de datos en servidor.
- Consultas preparadas mediante PDO.
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

- El contenido debe ser código real.
- No utilices pseudocódigo.
- No utilices marcadores TODO.
- Todos los archivos deben funcionar conjuntamente.
- No utilices rutas absolutas.
- Devuelve JSON válido.
- No incluyas fences Markdown.
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

    informe_carpeta = generar_informe_carpeta(
        archivos
    )

    ruta_informe = CARPETA / "informe_contenido.md"

    ruta_informe.write_text(
        informe_carpeta,
        encoding="utf-8"
    )

    print(
        f"\nInforme de contenido: {ruta_informe}"
    )

    prompt = f"""
Eres un auditor senior de software.

Tu trabajo consiste en evaluar una aplicación CRUD
generada por otra inteligencia artificial.

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
8. Comprueba la coherencia entre archivos.
9. Identifica funcionalidades incompletas.
10. Propón mejoras concretas.

IMPORTANTE:

No presupongas pruebas que no consten en el informe.

Diferencia claramente entre:

- Funcionalidad observada en el código.
- Funcionalidad comprobada mediante herramientas.
- Funcionalidad no verificada.

Devuelve exclusivamente un informe Markdown con:

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

Sé exigente.

Justifica todas las conclusiones.

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

    print(
        f"\nInforme de evaluación: {destino}"
    )

    return evaluacion


# PROGRAMA PRINCIPAL ###############################################

def main():
    print("=" * 60)
    print("JOCARSA | GENERADOR Y EVALUADOR DE CRUD")
    print("=" * 60)

    print("\nSelecciona una opción:")
    print("1.- Generar un nuevo CRUD y evaluarlo")
    print("2.- Evaluar el CRUD existente")

    opcion = input("\nOpción [1/2]: ").strip()

    if opcion == "1":
        objetivo = input(
            "\n¿Qué aplicación CRUD quieres crear?\n> "
        ).strip()

        if not objetivo:
            print("No has indicado ningún objetivo.")
            return

        CARPETA.mkdir(
            parents=True,
            exist_ok=True
        )

        (CARPETA / "objetivo.txt").write_text(
            objetivo,
            encoding="utf-8"
        )

        proyecto, archivos = agente_generador(
            objetivo
        )

        print("\nAplicación generada:")
        print(
            proyecto.get("nombre", "Sin nombre")
        )

    elif opcion == "2":
        ruta_objetivo = CARPETA / "objetivo.txt"

        if not ruta_objetivo.exists():
            print(
                "\nNo existe objetivo.txt."
            )
            return

        objetivo = ruta_objetivo.read_text(
            encoding="utf-8"
        )

        archivos = obtener_archivos_proyecto()

        if not archivos:
            print(
                "\nNo existen archivos para evaluar."
            )
            return

        print("\nProyecto existente encontrado.")

        for archivo in archivos:
            print(
                "  " + str(
                    archivo.relative_to(CARPETA)
                )
            )

    else:
        print("\nOpción no válida.")
        return

    # Una sola evaluación
    evaluacion = agente_evaluador(
        objetivo,
        archivos
    )

    print("\n========== RESULTADO ==========\n")

    print(evaluacion)

    print("\n" + "=" * 60)
    print("PROCESO FINALIZADO")
    print("=" * 60)

    print(f"\nCarpeta: {CARPETA}")
    print("Generaciones adicionales: 0")
    print("Evaluaciones adicionales: 0")


if __name__ == "__main__":
    try:
        main()

    except requests.RequestException as error:
        print(
            f"\nError de comunicación con la API externa: {error}"
        )

    except (ValueError, KeyError, TypeError) as error:
        print(
            f"\nError procesando el proyecto: {error}"
        )

    except OSError as error:
        print(
            f"\nError de archivos: {error}"
        )
