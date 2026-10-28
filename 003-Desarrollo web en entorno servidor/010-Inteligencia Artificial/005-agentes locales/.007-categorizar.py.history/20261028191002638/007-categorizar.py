
import os
import json
import time
import hashlib
import fitz
import requests
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================

CARPETA = "/home/josevicente/Escritorio"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "granite4.1:8b"

MAX_CARACTERES = 12000
TIMEOUT = 300

ARCHIVO_RESULTADOS = "clasificacion_pdfs.jsonl"
ARCHIVO_ERRORES = "errores_pdfs.jsonl"

# ============================================================
# CATEGORÍAS Y SUBCATEGORÍAS
# ============================================================

CATEGORIAS = {
    "Educación y docencia": [
        "Programaciones didácticas",
        "Materiales y apuntes",
        "Exámenes y actividades",
        "Evaluaciones y calificaciones",
        "Normativa educativa",
        "Horarios y planificación"
    ],
    "Alumnos y gestión académica": [
        "Expedientes y fichas",
        "Informes individuales",
        "Matrículas",
        "Asistencia y seguimiento",
        "Comunicaciones y tutorías"
    ],
    "Prácticas y empresas": [
        "Empresas colaboradoras",
        "Selección de alumnos",
        "Envíos de currículums",
        "Convenios y documentación",
        "Seguimiento de prácticas"
    ],
    "Informática y desarrollo": [
        "Programación y lenguajes",
        "Bases de datos",
        "Desarrollo web",
        "Sistemas y redes",
        "Inteligencia artificial",
        "Manuales técnicos"
    ],
    "Proyectos y productos": [
        "Proyectos JOCARSA",
        "Proyectos intermodulares",
        "Aplicaciones y herramientas",
        "Documentación funcional",
        "Identidad corporativa"
    ],
    "Administración y finanzas": [
        "Facturas emitidas",
        "Facturas recibidas",
        "Presupuestos",
        "Contratos y acuerdos",
        "Justificantes y pagos"
    ],
    "Laboral y profesional": [
        "Currículums",
        "Contratos laborales",
        "Vida laboral",
        "Certificados profesionales"
    ],
    "Legislación y normativa": [
        "BOE y legislación estatal",
        "Normativa autonómica",
        "Protección de datos",
        "Documentación legal"
    ],
    "Empresa y negocio": [
        "Clientes y proveedores",
        "Propuestas comerciales",
        "Informes empresariales",
        "Marketing y comunicación"
    ],
    "Material educativo general": [
        "Matemáticas",
        "Física y química",
        "Biología y salud",
        "Historia y humanidades",
        "Ejercicios y soluciones"
    ],
    "Personal y patrimonio": [
        "Documentación personal",
        "Vivienda y planos",
        "Gestiones particulares",
        "Ocio y otros documentos"
    ],
    "Archivo y pendientes": [
        "Sin clasificar",
        "Duplicados y versiones",
        "Documentos sin texto",
        "Documentación obsoleta"
    ]
}

# ============================================================
# UTILIDADES
# ============================================================

def guardar_jsonl(archivo, datos):
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(datos, ensure_ascii=False) + "\n"
        )


def cargar_procesados():
    procesados = set()

    if not os.path.exists(ARCHIVO_RESULTADOS):
        return procesados

    with open(
        ARCHIVO_RESULTADOS,
        "r",
        encoding="utf-8"
    ) as f:
        for linea in f:
            try:
                dato = json.loads(linea)
                if dato.get("ruta") and dato.get("firma"):
                    procesados.add(
                        (dato["ruta"], dato["firma"])
                    )
            except (json.JSONDecodeError, KeyError):
                continue

    return procesados


def firma_archivo(ruta):
    stat = os.stat(ruta)
    contenido = (
        f"{stat.st_size}:{stat.st_mtime_ns}"
    )
    return hashlib.sha256(
        contenido.encode()
    ).hexdigest()


# ============================================================
# EXTRAER TEXTO
# ============================================================

def extraer_texto(ruta):
    partes = []
    caracteres = 0
    paginas = 0

    with fitz.open(ruta) as pdf:
        total_paginas = len(pdf)

        for pagina in pdf:
            texto_pagina = pagina.get_text("text")

            if not texto_pagina.strip():
                continue

            restantes = MAX_CARACTERES - caracteres

            if restantes <= 0:
                break

            fragmento = texto_pagina[:restantes]
            partes.append(fragmento)

            caracteres += len(fragmento)
            paginas += 1

            if caracteres >= MAX_CARACTERES:
                break

    return {
        "texto": "\n".join(partes).strip(),
        "paginas_totales": total_paginas,
        "paginas_leidas": paginas,
        "caracteres": caracteres
    }


# ============================================================
# OLLAMA
# ============================================================

def analizar_documento(texto, nombre_archivo):
    categorias_json = json.dumps(
        CATEGORIAS,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
Eres un especialista en análisis y clasificación documental.

Debes analizar un documento y realizar dos tareas:

1. Escribir un resumen en español, en un único párrafo,
   sin listas ni títulos, destacando lo más importante.

2. Clasificar el documento en una única categoría
   y una única subcategoría.

CATEGORÍAS PERMITIDAS:

{categorias_json}

REGLAS OBLIGATORIAS:

- Utiliza exclusivamente las categorías indicadas.
- La subcategoría debe pertenecer a la categoría elegida.
- No inventes categorías.
- No inventes subcategorías.
- No dejes el resumen vacío.
- No devuelvas explicaciones adicionales.
- Clasifica según el contenido del documento.
- El nombre del archivo es información auxiliar.
- Si no puedes determinar la clasificación, utiliza
  "Archivo y pendientes" y "Sin clasificar".

Devuelve exclusivamente este objeto JSON:

{{
    "resumen": "Resumen del documento en un párrafo",
    "categoria": "Categoría exacta",
    "subcategoria": "Subcategoría exacta"
}}

NOMBRE DEL ARCHIVO:
{nombre_archivo}

CONTENIDO DEL DOCUMENTO:
{texto}
"""

    respuesta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
                "num_ctx": 16384,
                "num_predict": 900
            }
        },
        timeout=TIMEOUT
    )

    respuesta.raise_for_status()

    datos = respuesta.json()
    contenido = datos.get("response", "").strip()

    if not contenido:
        raise ValueError(
            "Ollama ha devuelto una respuesta vacía. "
            f"Motivo: {datos.get('done_reason')}"
        )

    try:
        resultado = json.loads(contenido)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON inválido de Ollama: {contenido[:500]}"
        ) from error

    if not isinstance(resultado, dict):
        raise ValueError(
            "Ollama no ha devuelto un objeto JSON"
        )

    resumen = resultado.get("resumen")
    categoria = resultado.get("categoria")
    subcategoria = resultado.get("subcategoria")

    if not isinstance(resumen, str) or not resumen.strip():
        raise ValueError(
            f"Ollama ha devuelto un resumen vacío: {resultado}"
        )

    if categoria not in CATEGORIAS:
        raise ValueError(
            f"Categoría no válida: {categoria}"
        )

    if subcategoria not in CATEGORIAS[categoria]:
        raise ValueError(
            f"Subcategoría no válida: {subcategoria}"
        )

    return {
        "resumen": " ".join(resumen.split()),
        "categoria": categoria,
        "subcategoria": subcategoria,
        "tokens_entrada": datos.get("prompt_eval_count", 0),
        "tokens_salida": datos.get("eval_count", 0),
        "duracion_ollama": round(
            datos.get("total_duration", 0) / 1_000_000_000,
            2
        )
    }


# ============================================================
# BUSCAR DOCUMENTOS
# ============================================================

def buscar_pdfs():
    archivos_pdf = []

    for raiz, carpetas, archivos in os.walk(CARPETA):
        for archivo in archivos:
            if archivo.lower().endswith(".pdf"):
                archivos_pdf.append(
                    os.path.join(raiz, archivo)
                )

    return sorted(archivos_pdf)


# ============================================================
# PROCESAMIENTO PRINCIPAL
# ============================================================

def procesar_pdfs():
    archivos_pdf = buscar_pdfs()
    procesados = cargar_procesados()

    total = len(archivos_pdf)
    correctos = 0
    errores = 0
    omitidos = 0

    print()
    print("=" * 80)
    print("CLASIFICADOR DOCUMENTAL CON OLLAMA")
    print("=" * 80)
    print(f"Carpeta: {CARPETA}")
    print(f"Modelo: {MODELO}")
    print(f"Máximo caracteres: {MAX_CARACTERES}")
    print(f"Documentos encontrados: {total}")
    print(f"Resultados anteriores: {len(procesados)}")
    print("=" * 80)
    print(flush=True)

    for indice, ruta in enumerate(archivos_pdf, 1):
        print("=" * 80)
        print(f"DOCUMENTO {indice} DE {total}")
        print("=" * 80)
        print(f"Archivo: {ruta}", flush=True)

        inicio = time.time()

        try:
            firma = firma_archivo(ruta)

            if (ruta, firma) in procesados:
                omitidos += 1
                print("Estado: YA PROCESADO")
                print()
                continue

            informacion = extraer_texto(ruta)
            texto = informacion["texto"]

            print(
                f"Texto extraído: {len(texto)} caracteres"
            )
            print(
                f"Páginas: {informacion['paginas_leidas']}"
                f"/{informacion['paginas_totales']}"
            )

            if not texto:
                resultado = {
                    "resumen": (
                        "No se ha podido extraer texto "
                        "del documento."
                    ),
                    "categoria": "Archivo y pendientes",
                    "subcategoria": "Documentos sin texto",
                    "tokens_entrada": 0,
                    "tokens_salida": 0,
                    "duracion_ollama": 0
                }
            else:
                print(
                    "Analizando con Ollama...",
                    flush=True
                )

                resultado = analizar_documento(
                    texto,
                    os.path.basename(ruta)
                )

            duracion = round(time.time() - inicio, 2)

            registro = {
                "ruta": ruta,
                "archivo": os.path.basename(ruta),
                "firma": firma,
                "fecha_analisis": datetime.now().isoformat(),
                "modelo": MODELO,
                "caracteres_analizados": len(texto),
                "paginas_totales": informacion["paginas_totales"],
                "resumen": resultado["resumen"],
                "categoria": resultado["categoria"],
                "subcategoria": resultado["subcategoria"],
                "duracion_segundos": duracion,
                "tokens_entrada": resultado["tokens_entrada"],
                "tokens_salida": resultado["tokens_salida"]
            }

            guardar_jsonl(
                ARCHIVO_RESULTADOS,
                registro
            )

            procesados.add((ruta, firma))
            correctos += 1

            print()
            print("RESUMEN:")
            print(resultado["resumen"])

            print()
            print("CLASIFICACIÓN:")
            print("Categoría:", resultado["categoria"])
            print("Subcategoría:", resultado["subcategoria"])

            print()
            print(f"Tiempo: {duracion} segundos")
            print(
                "Tokens:",
                resultado["tokens_entrada"],
                "entrada /",
                resultado["tokens_salida"],
                "salida"
            )

        except KeyboardInterrupt:
            print("\nProcesamiento interrumpido.")
            print("Los resultados anteriores están guardados.")
            break

        except Exception as error:
            errores += 1

            print()
            print("ERROR:", str(error), flush=True)

            guardar_jsonl(
                ARCHIVO_ERRORES,
                {
                    "ruta": ruta,
                    "fecha": datetime.now().isoformat(),
                    "error": str(error)
                }
            )

        print()
        print(
            f"PROGRESO: {indice}/{total} | "
            f"Correctos: {correctos} | "
            f"Errores: {errores} | "
            f"Omitidos: {omitidos}",
            flush=True
        )
        print()

    print("=" * 80)
    print("PROCESAMIENTO FINALIZADO")
    print("=" * 80)
    print(f"Total encontrados: {total}")
    print(f"Procesados correctamente: {correctos}")
    print(f"Errores: {errores}")
    print(f"Omitidos: {omitidos}")
    print(f"Resultados: {ARCHIVO_RESULTADOS}")
    print(f"Errores: {ARCHIVO_ERRORES}")
    print("=" * 80)


if __name__ == "__main__":
    procesar_pdfs()
