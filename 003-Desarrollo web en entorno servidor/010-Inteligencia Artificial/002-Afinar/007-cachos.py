
import os
import re
import json
import time
import math
import requests
from pathlib import Path
from datetime import timedelta

# ==========================================
# CONFIGURACIÓN
# ==========================================

CARPETA = Path("/var/www/html/clases/")

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODELO = "granite4.1:8b"

# Tamaño de fragmento en caracteres.
# 2500 caracteres suelen equivaler aproximadamente
# a 600-1000 tokens, dependiendo del texto.
TAMANO_FRAGMENTO = 2500
SOLAPAMIENTO = 200

# Contexto limitado para reducir uso de VRAM
NUM_CTX = 4096
NUM_PREDICT = 2048

TIMEOUT = 600

OMITIR_EXISTENTES = True

# Estimación inicial hasta disponer de mediciones.
SEGUNDOS_INICIALES_POR_CHUNK = 25

# Ventana de tiempos para la estimación dinámica
VENTANA_ESTIMACION = 30

# ==========================================
# UTILIDADES
# ==========================================

def formatear_tiempo(segundos):
    segundos = max(0, int(segundos))
    return str(timedelta(seconds=segundos))


def formatear_tamano(bytes_):
    if bytes_ < 1024:
        return f"{bytes_} B"
    if bytes_ < 1024**2:
        return f"{bytes_ / 1024:.1f} KB"
    return f"{bytes_ / 1024**2:.2f} MB"


def normalizar(texto):
    return re.sub(r"\s+", " ", texto.strip().lower())


# ==========================================
# FRAGMENTACIÓN
# ==========================================

def dividir_texto(texto):
    fragmentos = []
    inicio = 0

    while inicio < len(texto):
        fin = min(
            inicio + TAMANO_FRAGMENTO,
            len(texto)
        )

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
# FASE 1: ANÁLISIS PREVIO
# ==========================================

def analizar_documentos():

    documentos = []

    print("\n" + "=" * 75)
    print("FASE 1 - ANÁLISIS DE TODOS LOS DOCUMENTOS")
    print("=" * 75)

    total_caracteres = 0
    total_palabras = 0
    total_bytes = 0
    total_chunks = 0

    for raiz, carpetas, archivos in os.walk(CARPETA):
        carpetas.sort()

        for nombre in sorted(archivos):

            if not nombre.lower().endswith(".txt"):
                continue

            ruta = Path(raiz) / nombre
            salida = ruta.with_suffix(".jsonl")

            if OMITIR_EXISTENTES and salida.exists():
                print(f"[OMITIDO] {ruta}")
                continue

            try:
                texto = ruta.read_text(
                    encoding="utf-8",
                    errors="replace"
                )
            except Exception as e:
                print(f"[ERROR] {ruta}: {e}")
                continue

            if not texto.strip():
                continue

            fragmentos = dividir_texto(texto)

            if not fragmentos:
                continue

            caracteres = len(texto)
            palabras = len(texto.split())
            bytes_ = ruta.stat().st_size

            documento = {
                "ruta": ruta,
                "salida": salida,
                "fragmentos": fragmentos,
                "caracteres": caracteres,
                "palabras": palabras,
                "bytes": bytes_,
                "chunks": len(fragmentos)
            }

            documentos.append(documento)

            total_caracteres += caracteres
            total_palabras += palabras
            total_bytes += bytes_
            total_chunks += len(fragmentos)

            print(
                f"{str(ruta):65.65} "
                f"{len(fragmentos):5} chunks"
            )

    resumen = {
        "documentos": len(documentos),
        "caracteres": total_caracteres,
        "palabras": total_palabras,
        "bytes": total_bytes,
        "chunks": total_chunks
    }

    print("\n" + "-" * 75)
    print("RESUMEN DEL CORPUS")
    print("-" * 75)
    print("Documentos:", resumen["documentos"])
    print("Caracteres:", f"{total_caracteres:,}")
    print("Palabras:", f"{total_palabras:,}")
    print("Tamaño:", formatear_tamano(total_bytes))
    print("Fragmentos:", f"{total_chunks:,}")

    estimacion = (
        total_chunks * SEGUNDOS_INICIALES_POR_CHUNK
    )

    print(
        "Estimación inicial:",
        formatear_tiempo(estimacion)
    )
    print(
        "(Se recalculará con tiempos reales)"
    )

    return documentos, resumen


# ==========================================
# EXTRAER JSON
# ==========================================

def extraer_json(respuesta):

    respuesta = respuesta.strip()

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
            for clave in (
                "preguntas", "pares", "items"
            ):
                if isinstance(datos.get(clave), list):
                    return datos[clave]

    except json.JSONDecodeError:
        pass

    inicio = respuesta.find("[")
    fin = respuesta.rfind("]")

    if inicio >= 0 and fin > inicio:
        try:
            datos = json.loads(
                respuesta[inicio:fin + 1]
            )

            if isinstance(datos, list):
                return datos

        except json.JSONDecodeError:
            pass

    return []


# ==========================================
# OLLAMA
# ==========================================

def generar_preguntas(texto):

    prompt = f"""
Convierte el documento en el máximo número
posible de pares de pregunta y respuesta.

INSTRUCCIONES:

- Extrae todos los conceptos relevantes.
- Genera preguntas variadas.
- Incluye definiciones, funcionamiento,
  procedimientos, ejemplos y comparaciones.
- Las respuestas deben ser independientes.
- No inventes información.
- No repitas preguntas.
- Devuelve exclusivamente JSON válido.

FORMATO:

[
  {{
    "pregunta": "¿Qué es ...?",
    "respuesta": "..."
  }}
]

DOCUMENTO:

{texto}
"""

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": "30m",
        "options": {
            "temperature": 0.2,
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT
        }
    }

    inicio = time.monotonic()

    try:
        respuesta = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=TIMEOUT
        )

        respuesta.raise_for_status()
        datos = respuesta.json()

        pares = extraer_json(
            datos.get("response", "")
        )

        duracion = time.monotonic() - inicio

        return pares, duracion, datos, True

    except Exception as e:
        duracion = time.monotonic() - inicio
        print("\nError Ollama:", e)

        return [], duracion, {}, False


# ==========================================
# ESTIMADOR DINÁMICO
# ==========================================

class Estimador:

    def __init__(self, total_chunks):

        self.total_chunks = total_chunks
        self.procesados = 0
        self.tiempos = []

        self.inicio = time.monotonic()

    def registrar(self, duracion):

        self.procesados += 1

        self.tiempos.append(duracion)

        if len(self.tiempos) > VENTANA_ESTIMACION:
            self.tiempos.pop(0)

    def calcular(self):

        transcurrido = (
            time.monotonic() - self.inicio
        )

        restantes = (
            self.total_chunks - self.procesados
        )

        if self.tiempos:
            promedio = (
                sum(self.tiempos) / len(self.tiempos)
            )
        else:
            promedio = SEGUNDOS_INICIALES_POR_CHUNK

        eta = restantes * promedio

        porcentaje = (
            self.procesados / self.total_chunks * 100
            if self.total_chunks else 100
        )

        return {
            "porcentaje": porcentaje,
            "restantes": restantes,
            "promedio": promedio,
            "eta": eta,
            "transcurrido": transcurrido
        }


# ==========================================
# FASE 2: PROCESAMIENTO
# ==========================================

def procesar_documentos(documentos, resumen):

    estimador = Estimador(resumen["chunks"])

    total_pares = 0
    archivos_completados = 0
    archivos_incompletos = 0

    print("\n" + "=" * 75)
    print("FASE 2 - GENERACIÓN DE DATASETS")
    print("=" * 75)

    for numero_documento, documento in enumerate(
        documentos, start=1
    ):

        ruta = documento["ruta"]
        salida = documento["salida"]
        fragmentos = documento["fragmentos"]

        print("\n" + "=" * 75)
        print(
            f"DOCUMENTO {numero_documento}/"
            f"{len(documentos)}"
        )
        print("Archivo:", ruta)
        print("Fragmentos:", len(fragmentos))
        print("=" * 75)

        preguntas_vistas = set()
        pares_documento = 0
        errores_documento = 0

        temporal = salida.with_suffix(".jsonl.tmp")

        with open(
            temporal,
            "w",
            encoding="utf-8"
        ) as archivo_salida:

            for indice, fragmento in enumerate(
                fragmentos, start=1
            ):

                pares, duracion, datos, correcto = (
                    generar_preguntas(fragmento)
                )

                nuevos = 0

                if not correcto or not pares:
                    errores_documento += 1

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

                    nuevos += 1
                    pares_documento += 1
                    total_pares += 1

                archivo_salida.flush()

                estimador.registrar(duracion)
                estado = estimador.calcular()

                # Métricas reales de Ollama
                tokens_salida = datos.get(
                    "eval_count", 0
                )

                ns_evaluacion = datos.get(
                    "eval_duration", 0
                )

                velocidad = (
                    tokens_salida /
                    (ns_evaluacion / 1e9)
                    if ns_evaluacion else 0
                )

                print(
                    f"\n[{estado['porcentaje']:6.2f}%] "
                    f"Chunk {indice}/{len(fragmentos)}"
                )

                print(
                    f"  Duración: {duracion:.1f} s"
                    f" | Velocidad: {velocidad:.1f} tok/s"
                )

                print(
                    f"  Pares nuevos: {nuevos}"
                    f" | Total: {total_pares}"
                )

                print(
                    f"  Chunks: {estimador.procesados:,}"
                    f"/{estimador.total_chunks:,}"
                )

                print(
                    "  Transcurrido:",
                    formatear_tiempo(
                        estado["transcurrido"]
                    )
                )

                print(
                    "  ETA restante:",
                    formatear_tiempo(
                        estado["eta"]
                    )
                )

                print(
                    "  Finalización estimada:",
                    time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(
                            time.time() + estado["eta"]
                        )
                    )
                )

        if errores_documento == 0:
            os.replace(temporal, salida)
            archivos_completados += 1
            print("\nGUARDADO:", salida)
        else:
            archivos_incompletos += 1
            print(
                "\nINCOMPLETO:",
                errores_documento,
                "fragmentos fallidos."
            )
            print("Temporal:", temporal)

        print(
            "Pares de este documento:",
            pares_documento
        )

    print("\n" + "=" * 75)
    print("PROCESO FINALIZADO")
    print("=" * 75)
    print("Archivos completados:", archivos_completados)
    print("Archivos incompletos:", archivos_incompletos)
    print("Pares generados:", total_pares)
    print(
        "Tiempo total:",
        formatear_tiempo(
            time.monotonic() - estimador.inicio
        )
    )


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

def main():

    documentos, resumen = analizar_documentos()

    if not documentos:
        print("No hay documentos pendientes.")
        return

    procesar_documentos(documentos, resumen)


if __name__ == "__main__":
    main()
