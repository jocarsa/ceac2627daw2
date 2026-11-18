# Casa IA · Flask + Ollama

## Instalación

```bash
ollama pull qwen2.5:3b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000

## Diagnóstico de errores 503

Comprueba Ollama con:

```bash
curl http://127.0.0.1:11434/api/tags
ollama list
curl http://127.0.0.1:5000/api/estado
```

En Linux, si Ollama no está iniciado, prueba `ollama serve` en otra terminal o `sudo systemctl start ollama` si lo tienes instalado como servicio.

El backend limita a una inferencia simultánea, aplica una ventana de caché de 12 segundos y el frontend consulta aproximadamente cada 20 segundos, solo cuando no está caminando. Los fallos aplican 15 segundos de espera. El estado 429 indica que Ollama está ocupado; 503 muestra el error concreto en el panel y en los logs de Flask.

## Opciones

- `OLLAMA_MODEL=qwen2.5:3b`
- `OLLAMA_URL=http://127.0.0.1:11434/api/chat`
- `AI_COOLDOWN=12`

Se puede añadir `sprite.png` junto a `index.html`; si no está, se dibuja un personaje provisional.
