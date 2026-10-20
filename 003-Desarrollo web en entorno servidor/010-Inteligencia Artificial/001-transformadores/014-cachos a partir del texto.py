
import requests
import json
import re
import argparse
import time
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "granite4.1:8b"

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

OUTPUT_FILE = "training_pairs.jsonl"


# ----------------------------------------
# 1. Leer archivo
# ----------------------------------------

def leer_archivo(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        return archivo.read()


# ----------------------------------------
# 2. Limpiar texto
# ----------------------------------------

def limpiar_texto(texto):
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


# ----------------------------------------
# 3. Dividir en chunks
# ----------------------------------------

def crear_chunks(texto, tamano=1500, overlap=200):

    if tamano <= 0 or overlap < 0 or overlap >= tamano:
        raise ValueError(
            "El tamaño debe ser positivo y overlap menor que tamaño"
        )

    chunks = []
    inicio = 0

    while inicio < len(texto):

        fin = min(inicio + tamano, len(texto))

        # Intentar cortar al final de una frase
        if fin < len(texto):
            segmento = texto[inicio:fin]

            posiciones = [
                segmento.rfind(". "),
                segmento.rfind("? "),
                segmento.rfind("! ")
            ]

            corte = max(posiciones)

            if corte > tamano // 2:
                fin = inicio + corte + 1

        chunk = texto[inicio:fin].strip()

        if chunk:
            chunks.append(chunk)

        if fin >= len(texto):
            break

        inicio = max(inicio + 1, fin - overlap)

    return chunks


# ----------------------------------------
# 4. Generar pareja semántica
# ----------------------------------------

def generar_pareja(parrafo):

    prompt = f"""
You are creating high-quality training data
for a semantic embedding model.

Read this source paragraph:

<source>
{parrafo}
</source>

Generate exactly TWO different sentences in Spanish.

Requirements:
- Both sentences must express the same meaning.
- Use different vocabulary and grammatical structures.
- Preserve important facts.
- Both sentences must be independently understandable.
- Do not invent information.
- Do not introduce contradictions.
- Keep the meaning of both sentences equivalent.
- Return ONLY valid JSON.

Required JSON format:
{{
    "sentence1": "...",
    "sentence2": "..."
}}
"""

    respuesta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.5,
                "num_ctx": 8192
            }
        },
        timeout=300
    )

    respuesta.raise_for_status()

    contenido = respuesta.json()["response"]
    datos = json.loads(contenido)

    frase1 = datos.get("sentence1", "").strip()
    frase2 = datos.get("sentence2", "").strip()

    if not frase1 or not frase2:
        raise ValueError("El modelo devolvió frases vacías")

    if frase1 == frase2:
        raise ValueError("Las frases son idénticas")

    return {
        "sentence1": frase1,
        "sentence2": frase2
    }


# ----------------------------------------
# 5. Procesar archivo
# ----------------------------------------

def procesar_archivo(ruta, salida, tamano, overlap):

    print("Leyendo archivo:", ruta)

    texto = leer_archivo(ruta)
    texto = limpiar_texto(texto)

    chunks = crear_chunks(texto, tamano, overlap)

    print("Caracteres:", len(texto))
    print("Chunks generados:", len(chunks))
    print("Modelo:", MODEL)
    print("-" * 60)

    # Recuperación de progreso:
    # archivo de estado independiente
    estado = Path(str(salida) + ".progress")

    inicio = 0

    if estado.exists():
        try:
            inicio = int(estado.read_text().strip())
        except ValueError:
            inicio = 0

    inicio = max(0, min(inicio, len(chunks)))

    print("Continuando desde chunk:", inicio + 1)

    for indice in range(inicio, len(chunks)):

        chunk = chunks[indice]

        print(
            f"\n[{indice + 1}/{len(chunks)}] "
            f"Procesando {len(chunk)} caracteres"
        )

        try:
            pareja = generar_pareja(chunk)

            print("Frase 1:", pareja["sentence1"])
            print("Frase 2:", pareja["sentence2"])

            registro = {
                "source_file": str(ruta),
                "chunk_id": indice,
                "sentence1": pareja["sentence1"],
                "sentence2": pareja["sentence2"]
            }

            with open(salida, "a", encoding="utf-8") as archivo:
                archivo.write(
                    json.dumps(
                        registro,
                        ensure_ascii=False
                    ) + "\n"
                )

            # Guardar progreso tras escribir el resultado
            estado.write_text(str(indice + 1))

        except Exception as error:
            print("ERROR:", error)
            print("Se conserva el progreso anterior.")
            break

    else:
        print("\nProceso completado.")
        print("Dataset:", salida)


# ----------------------------------------
# 6. Programa principal
# ----------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "archivo",
        help="Archivo TXT de entrada"
    )

    parser.add_argument(
        "--output",
        default=OUTPUT_FILE
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=CHUNK_OVERLAP
    )

    args = parser.parse_args()

    procesar_archivo(
        args.archivo,
        args.output,
        args.chunk_size,
        args.overlap
    )
