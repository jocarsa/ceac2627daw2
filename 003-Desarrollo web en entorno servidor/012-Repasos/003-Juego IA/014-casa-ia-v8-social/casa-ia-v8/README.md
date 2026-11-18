# Casa IA v8 — convivencia y memoria

## Instalación

```bash
ollama pull qwen2.5:7b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000

## Novedades

- Hasta ocho personajes con nombres individuales elegidos mediante Ollama (respaldo local si el modelo no responde).
- Cada personaje tiene necesidades, objetivos, pensamientos, rutas y memoria SQLite propias.
- Percepción de personajes cercanos con comprobación de línea de visión.
- Encuentros y diálogos de dos turnos almacenados para ambos participantes.
- Detección de colisiones entre personajes, espera y maniobras de cesión en pasos estrechos.
- Tras una espera prolongada, los personajes pueden cruzarse sin atravesar paredes ni muebles.
- Visualización de rutas activada por defecto.
- Se conserva la base `memoria.sqlite` si se copia desde una versión anterior.

## API

- `GET /api/estado`
- `GET /api/memoria?agente_id=agente-1`
- `POST /api/decidir`
- `POST /api/nombre`
- `POST /api/dialogar`
- `POST /api/evento`

## Notas

Una sola inferencia Ollama a la vez; si está ocupado, los diálogos usan respuestas locales de respaldo. El sistema de identidad utiliza IDs por personaje; si se crea una nueva partida con los mismos IDs, recupera los nombres anteriores. Para un guardado completo de posición/estado se necesitaría persistir también el mundo.
