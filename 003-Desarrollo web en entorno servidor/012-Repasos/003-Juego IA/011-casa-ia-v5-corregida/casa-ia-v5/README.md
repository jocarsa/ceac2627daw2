# Casa IA v5 — decisiones coherentes y memoria SQLite

Partiendo de la versión 4 proporcionada, se mantiene Flask, la navegación A*, los bocadillos y SQLite.

## Cambios
- El servidor calcula prioridades ponderadas: sed 1.3, pipí 1.2, cansancio 1.0, aburrimiento 0.7.
- Una necesidad inferior a 12 queda fuera de los destinos elegibles.
- Histéresis: el personaje mantiene su objetivo hasta que una alternativa lo supera suficientemente.
- Ollama solo redacta el pensamiento sobre la acción validada. Si falla, se utiliza una frase local y la simulación continúa.
- Se siguen registrando decisiones y diálogos en `memoria.sqlite`.

## Instalación
```bash
ollama pull qwen2.5:3b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Abrir http://127.0.0.1:5000

Si Ollama se ejecuta en otro equipo, definir `OLLAMA_URL` con la URL de su API `/api/chat`.
