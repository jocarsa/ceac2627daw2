
import os
import json
import re
import time
import requests
from pathlib import Path

# ==========================================
# CONFIGURACIÓN
# ==========================================

CARPETA = "/var/www/html/clases/"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODELO = "granite4.1:8b"

TAMANO_FRAGMENTO = 6000
SOLAPAMIENTO = 500
TIMEOUT = 600

# Si es True, conserva los JSONL existentes
OMITIR_EXISTENTES = True

# ==========================================
# DIVIDIR TEXTO EN FRAGMENTOS
# ==========================================

def dividir_texto(texto):
    fragmentos = []

    inicio = 0

    while inicio < len(texto):
        fin = min(inicio + TAMANO_FRAGMENTO, len(texto))

        if fin < len(texto):
            corte = texto.rfind("\n", inicio, fin)

            if corte > inicio + TAMANO_FRAGMENTO // 2:
                fin = corte

        fragmento = texto[inicio:fin].strip()

        if fragmento:
            fragmentos.append(fragmento)

        if fin >= len(texto):
            break

        inicio = max(inicio + 1, fin - SOLAPAMIENTO)

    return fragmentos


# ==========================================
# EXTRAER JSON DE LA RESPUESTA
# ==========================================

def extraer_json(respuesta):
    respuesta = respuesta.strip()

    # Eliminar posibles bloques markdown
    respuesta = re.sub(
        r"^```(?:json)?\s*",
        "",
        respuesta
    )

    respuesta = re.sub(
        r"\s*```$",
        "",
        respuesta
    )

    try:
        datos = json.loads(respuesta)

        if isinstance(datos, list):
            return datos

        if isinstance(datos, dict):
            for clave in ("preguntas", "pares", "items"):
                if isinstance(datos.get(clave), list):
                    return datos[clave]

    except json.JSONDecodeError:
        pass

    # Intentar recuperar un array JSON
    inicio = respuesta.find("[")
    fin = respuesta.rfind("]")

    if inicio != -1 and fin > inicio:
        try:
            datos = json.loads(respuesta[inicio:fin + 1])

            if isinstance(datos, list):
                return datos

        except json.JSONDecodeError:
            pass

    return []


# ==========================================
# GENERAR PREGUNTAS Y RESPUESTAS
# ==========================================

def generar_preguntas(texto):

    prompt = f"""
Eres un experto en creación de datasets de
entrenamiento para modelos de lenguaje.

Tu tarea es convertir el siguiente documento
en el MAYOR NÚMERO POSIBLE de pares de
pregunta y respuesta.

REGLAS:

1. Extrae todos los conceptos, definiciones,
   procedimientos, ejemplos y relaciones.

2. Genera preguntas específicas y variadas.

3. Cada respuesta debe ser autónoma,
   clara, correcta y suficientemente detallada.

4. No inventes información que no esté
   respaldada por el documento.

5. No repitas preguntas equivalentes.

6. Incluye preguntas sobre:
   - Definiciones
   - Características
   - Funcionamiento
   - Comparaciones
   - Ejemplos
   - Procedimientos
   - Causas y consecuencias
   - Aplicaciones prácticas

7. Genera tantos pares útiles como permita
   el contenido, sin establecer un límite fijo.

8. Devuelve EXCLUSIVAMENTE un array JSON válido.

FORMATO OBLIGATORIO:

[
  {{
    "pregunta": "¿Qué es ...?",
    "respuesta": "..."
  }},
  {{
    "pregunta": "¿Cómo funciona ...?",
    "respuesta": "..."
  }}
]

DOCUMENTO:

<documento>
{texto}
</documento>
"""

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.3,
            "num_ctx": 16384,
            "num_predict": 8192
        }
    }

    try:
        respuesta = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=TIMEOUT
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        contenido = datos.get("response", "")

        return extraer_json(contenido)

    except Exception as error:
        print("Error Ollama:", error)
        return None


# ==========================================
# NORMALIZAR PREGUNTAS
# ==========================================

def normalizar(texto):
    return re.sub(
        r"\s+",
        " ",
        texto.strip().lower()
    )


# ==========================================
# PROCESAR UN ARCHIVO
# ==========================================

def procesar_archivo(ruta):

    ruta = Path(ruta)

    salida = ruta.with_suffix(".jsonl")

    if OMITIR_EXISTENTES and salida.exists():
        print("Omitido:", ruta)
        return 0

    print("\n====================================")
    print("Procesando:", ruta)
    print("====================================")

    try:
        texto = ruta.read_text(
            encoding="utf-8",
            errors="replace"
        )
    except Exception as error:
        print("Error leyendo:", error)
        return 0

    if not texto.strip():
        print("Archivo vacío")
        return 0

    fragmentos = dividir_texto(texto)

    print("Fragmentos:", len(fragmentos))

    preguntas_vistas = set()
    total = 0
    hubo_error = False

    # Temporal para no dejar resultados incompletos
    temporal = salida.with_suffix(".jsonl.tmp")

    try:
        with open(
            temporal,
            "w",
            encoding="utf-8"
        ) as archivo_salida:

            for indice, fragmento in enumerate(
                fragmentos, start=1
            ):

                print(
                    f"Fragmento {indice}/{len(fragmentos)}",
                    end=" ",
                    flush=True
                )

                inicio = time.time()

                pares = generar_preguntas(fragmento)

                if pares is None or not pares:
                    print("Sin resultado válido")
                    hubo_error = True
                    continue

                nuevos = 0

                for par in pares:

                    if not isinstance(par, dict):
                        continue

                    pregunta = str(
                        par.get("pregunta", "")
                    ).strip()

                    respuesta = str(
                        par.get("respuesta", "")
                    ).strip()

                    if not pregunta or not respuesta:
                        continue

                    clave = normalizar(pregunta)

                    if clave in preguntas_vistas:
                        continue

                    preguntas_vistas.add(clave)

                    # Formato de entrenamiento conversacional
                    registro = {
                        "messages": [
                            {
                                "role": "user",
                                "content": pregunta
                            },
                            {
                                "role": "assistant",
                                "content": respuesta
                            }
                        ]
                    }

                    archivo_salida.write(
                        json.dumps(
                            registro,
                            ensure_ascii=False
                        ) + "\n"
                    )

                    archivo_salida.flush()

                    nuevos += 1
                    total += 1

                duracion = time.time() - inicio

                print(
                    f"-> {nuevos} pares "
                    f"({duracion:.1f} s)"
                )

        if hubo_error:
            print(
                "Procesamiento incompleto. "
                "Temporal conservado:",
                temporal
            )
        else:
            os.replace(temporal, salida)
            print("Guardado:", salida)

    except Exception as error:
        print("Error procesando:", error)
        return 0

    print("Total de pares:", total)

    return total


# ==========================================
# RECORRER TODOS LOS TXT
# ==========================================

def main():

    inicio_global = time.time()

    total_archivos = 0
    total_pares = 0

    for raiz, carpetas, archivos in os.walk(CARPETA):

        carpetas.sort()

        for archivo in sorted(archivos):

            if not archivo.lower().endswith(".txt"):
                continue

            ruta = os.path.join(raiz, archivo)

            total_archivos += 1

            pares = procesar_archivo(ruta)

            total_pares += pares

    duracion = time.time() - inicio_global

    print("\n====================================")
    print("PROCESO FINALIZADO")
    print("====================================")
    print("Archivos encontrados:", total_archivos)
    print("Pares generados:", total_pares)
    print("Tiempo total:", round(duracion, 2), "s")


if __name__ == "__main__":
    main()
