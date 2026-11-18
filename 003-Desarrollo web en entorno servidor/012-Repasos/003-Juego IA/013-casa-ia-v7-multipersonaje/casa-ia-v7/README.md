# Casa IA v7 — varios personajes

## Instalar

```bash
ollama pull qwen2.5:7b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir http://127.0.0.1:5000

## Funcionamiento

- Tres personajes inicialmente. Botones `+ Personaje` y `− Personaje` (máximo ocho).
- Selecciona un personaje en el panel para ver sus necesidades, decisiones y memoria individual.
- Cada personaje mantiene un objetivo y su propio plan de navegación.
- Las rutas aparecen dibujadas en cian desde el principio.
- El backend almacena `agente_id` en la tabla `eventos` de SQLite y consulta únicamente la memoria del agente correspondiente.
- Ollama es compartido y se limita a una generación concurrente. Si está ocupado o falla, el personaje sigue funcionando con frases predeterminadas y decisiones basadas en prioridades.
- Puedes elegir otro modelo con `OLLAMA_MODEL=qwen2.5:3b python app.py`.

## Notas

Los personajes evitan ocupar exactamente la misma posición, pero la navegación multiagente no incorpora todavía reservas de pasillos ni negociación de prioridades; podrían esperar uno al otro en lugares estrechos.

La memoria de eventos persiste entre ejecuciones. Las necesidades y posiciones se reinician al recargar la página.
