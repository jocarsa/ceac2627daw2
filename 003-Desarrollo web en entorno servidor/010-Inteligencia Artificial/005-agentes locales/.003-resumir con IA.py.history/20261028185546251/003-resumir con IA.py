import fitz
import requests

# Abrir PDF
pdf = fitz.open("/home/josevicente/Escritorio/informe_alumnos_seleccionados_2026-10-28.pdf")

# Extraer texto
texto = ""

for pagina in pdf:
    texto += pagina.get_text() + "\n"

pdf.close()

# Preparar consulta
prompt = f"""
Analiza el siguiente documento y genera un resumen en español.

El resumen debe:
- Explicar de qué trata el documento.
- Identificar los datos más importantes.
- Destacar conclusiones relevantes.
- Ser claro, estructurado y conciso.

DOCUMENTO:
{texto}
"""

# Consultar Ollama local
respuesta = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "granite4.1:8b",
        "prompt": prompt,
        "stream": False
    },
    timeout=600
)

respuesta.raise_for_status()

# Mostrar resultado
print("\n===== RESUMEN DEL DOCUMENTO =====\n")
print(respuesta.json()["response"])