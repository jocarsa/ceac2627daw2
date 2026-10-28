
import os
import json
import fitz
import requests

# Configuración
CARPETA = "/home/josevicente/Escritorio"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "granite4.1:8b"

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


def extraer_texto(ruta):
    with fitz.open(ruta) as pdf:
        return "\n".join(
            pagina.get_text() for pagina in pdf
        ).strip()


def analizar_documento(texto):
    prompt = f"""
Analiza el siguiente documento PDF.

Realiza estas tareas:

1. Resume el documento en español en un único párrafo,
   sin listas ni títulos.
2. Identifica su categoría principal.
3. Identifica una única subcategoría.

Debes seleccionar EXCLUSIVAMENTE una categoría y una
subcategoría de esta estructura:

{json.dumps(CATEGORIAS, ensure_ascii=False, indent=2)}

Reglas:
- No inventes categorías ni subcategorías.
- La subcategoría debe pertenecer a la categoría elegida.
- Clasifica según el contenido, no según el nombre.
- Si no puedes clasificarlo, utiliza
  "Archivo y pendientes" / "Sin clasificar".
- Devuelve exclusivamente un JSON válido.

Formato obligatorio:

{{
    "resumen": "Resumen en un único párrafo",
    "categoria": "Categoría exacta",
    "subcategoria": "Subcategoría exacta"
}}

DOCUMENTO:

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
                "temperature": 0
            }
        },
        timeout=600
    )

    respuesta.raise_for_status()

    resultado = json.loads(
        respuesta.json()["response"]
    )

    categoria = resultado.get("categoria", "")
    subcategoria = resultado.get("subcategoria", "")

    # Validar clasificación
    if (
        categoria not in CATEGORIAS
        or subcategoria not in CATEGORIAS[categoria]
    ):
        resultado["categoria"] = "Archivo y pendientes"
        resultado["subcategoria"] = "Sin clasificar"

    return resultado


def procesar_pdfs():
    archivos_pdf = []

    # Buscar todos los PDF recursivamente
    for raiz, carpetas, archivos in os.walk(CARPETA):
        for archivo in archivos:
            if archivo.lower().endswith(".pdf"):
                archivos_pdf.append(
                    os.path.join(raiz, archivo)
                )

    archivos_pdf.sort()

    total = len(archivos_pdf)

    print(f"\nSe han encontrado {total} archivos PDF.\n")

    for indice, ruta in enumerate(archivos_pdf, start=1):
        print("=" * 80)
        print(f"DOCUMENTO {indice} DE {total}")
        print("=" * 80)
        print(f"Archivo: {ruta}\n", flush=True)

        try:
            texto = extraer_texto(ruta)

            if not texto:
                resultado = {
                    "resumen": "No se ha podido extraer texto del PDF.",
                    "categoria": "Archivo y pendientes",
                    "subcategoria": "Documentos sin texto"
                }
            else:
                resultado = analizar_documento(texto)

            print("RESUMEN:")
            print(resultado.get("resumen", ""))

            print("\nCLASIFICACIÓN:")
            print("Categoría:", resultado["categoria"])
            print("Subcategoría:", resultado["subcategoria"])

        except Exception as error:
            print(f"ERROR: {error}")

        print()

    print("=" * 80)
    print("PROCESAMIENTO FINALIZADO")
    print(f"Total de archivos encontrados: {total}")
    print("=" * 80)


if __name__ == "__main__":
    procesar_pdfs()
