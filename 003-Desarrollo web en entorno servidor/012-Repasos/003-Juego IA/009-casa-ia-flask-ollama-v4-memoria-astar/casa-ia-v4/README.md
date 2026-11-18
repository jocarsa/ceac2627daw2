# Casa IA v4 — Ollama + Flask + A* + SQLite

## Ejecutar

```bash
ollama pull qwen2.5:3b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000 . Ollama debe estar iniciado en localhost:11434.

## Arquitectura

- `app.py`: Flask, decisiones Ollama, memoria persistente SQLite (`memoria.sqlite`).
- `index.html`: casa, controles, necesidades, bocadillos y A* con rejilla de 4 px y colisiones geométricas.
- `sprite.png`: opcional, se utiliza un personaje provisional si falta.

## Memoria

SQLite se crea automáticamente. Tabla `eventos`: fecha UTC, tipo (decision/habla/llegada/bloqueo/accion/inicio), habitación, destino, acción, mensaje, necesidades JSON. El prompt recibe los 10 últimos eventos. La interfaz muestra los últimos 12.

- `GET /api/memoria?limit=20`: consulta el historial.
- `POST /api/evento`: guarda un evento.
- `POST /api/decidir`: consulta Ollama y registra la decisión.
- `GET /api/estado`: comprueba el modelo.

La base SQLite persiste entre reinicios. No se incluyen datos de prueba en el ZIP.

## Notas

La navegación A* utiliza una cuadrícula de 4 px, movimiento en 8 direcciones, verificación de diagonales, conexión del origen exacto a nodos válidos y suavizado por visibilidad. Para inspeccionarla pulsa `Mostrar ruta`. No se ha probado una ejecución real con Ollama.
