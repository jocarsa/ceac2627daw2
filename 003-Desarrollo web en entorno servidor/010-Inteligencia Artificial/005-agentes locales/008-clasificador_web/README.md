# Clasificador documental — simulación web

Instala dependencias:

```bash
pip install -r requirements.txt
```

Asegúrate de tener Ollama ejecutándose y el modelo `granite4.1:8b` disponible.

Inicia el servidor:

```bash
python3 app.py
```

Abre http://localhost:5000

La carpeta de origen se configura en `clasificador_original.py`, variable `CARPETA`.
Los resultados se guardan en `clasificacion_pdfs.jsonl` dentro de esta carpeta.
La clasificación es una simulación: **no se mueve ni se modifica ningún PDF**.
Al reanudar, se omiten los documentos cuya ruta y firma ya estén guardadas.
