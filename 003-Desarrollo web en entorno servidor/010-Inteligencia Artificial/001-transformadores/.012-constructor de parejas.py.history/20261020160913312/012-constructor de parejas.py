
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "granite4.1:8b"


def generar_pareja(parrafo):

    prompt = f"""
You are creating training data for a semantic embedding model.

Read the following paragraph:

{parrafo}

Generate exactly TWO different sentences in Spanish.

Requirements:
- Both sentences must express the same semantic meaning.
- Use different words and grammatical structures.
- Preserve the important facts from the paragraph.
- Each sentence must be understandable independently.
- Do not add information.
- Return ONLY a JSON object.

Format:
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
                "temperature": 0.7
            }
        },
        timeout=300
    )

    respuesta.raise_for_status()

    contenido = respuesta.json()["response"]
    datos = json.loads(contenido)

    return datos


if __name__ == "__main__":

    parrafo = """
    Los modelos de inteligencia artificial utilizan
    redes neuronales para aprender patrones a partir
    de grandes cantidades de información.
    """

    resultado = generar_pareja(parrafo)

    print("Sentence 1:")
    print(resultado["sentence1"])

    print("\nSentence 2:")
    print(resultado["sentence2"])

    # Guardar para entrenamiento
    with open("training_pairs.jsonl", "a", encoding="utf-8") as archivo:
        archivo.write(
            json.dumps(resultado, ensure_ascii=False) + "\n"
        )
