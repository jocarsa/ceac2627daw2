import fitz
import requests

pdf = fitz.open("/home/josevicente/Escritorio/informe_alumnos_seleccionados_2026-10-28.pdf")
texto = "\n".join(pagina.get_text() for pagina in pdf)
pdf.close()

respuesta = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "granite4.1:8b",
        "prompt": f"Resume el siguiente documento en español, en un único párrafo, sin listas ni títulos, destacando la información más importante:\n\n{texto}",
        "stream": False
    },
    timeout=600
)

respuesta.raise_for_status()
print(respuesta.json()["response"])