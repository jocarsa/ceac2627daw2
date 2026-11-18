# Casa IA v11 — cuatro casas 2×2

Se elimina el panel derecho. En la pantalla principal aparecen cuatro casas en una cuadrícula 2×2. Cada casa ejecuta su propia simulación con dos personajes, memoria SQLite diferenciada por casa y arrastre con el ratón.

## Arranque

```bash
ollama pull qwen2.5:7b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir http://127.0.0.1:5000

La configuración de intervalo de IA permanece en el código de cada casa (valor por defecto 20 s) y se conserva en localStorage. Las casas son simulaciones separadas: los personajes no pasan de una a otra. La memoria se guarda en `memoria.sqlite`.
