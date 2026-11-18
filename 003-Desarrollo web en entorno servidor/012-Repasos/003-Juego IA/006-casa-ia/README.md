# Casa IA local

Simulador de vida en Canvas 512×512, backend Flask y decisiones de un modelo Ollama local. Las decisiones se consultan cada 5 segundos; JavaScript ejecuta rutas A* y actualiza cuatro necesidades.

## Instalación (Ubuntu)

```bash
ollama pull qwen2.5:3b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Ollama debe estar ejecutándose (`ollama serve` si no funciona como servicio). Abre http://127.0.0.1:5000.

Para cambiar el modelo: `OLLAMA_MODEL=gemma3:4b python app.py` (descárgalo antes). Para un servidor Ollama distinto: `OLLAMA_URL=http://127.0.0.1:11434/api/chat`.

## Controles

- IA activada por defecto. Botón **IA** para alternar con movimiento manual.
- En modo manual: WASD o flechas.
- Botón **Decidir ahora** para pedir una decisión adicional.
- Botón **Colisiones** o tecla C para diagnóstico.

El personaje se representa con pixel art generado por canvas si no hay sprite.png. Puedes añadir tu propio sprite.png (32×32 píxeles recomendado) en esta carpeta.

## Reglas

- Sed: cocina; pipí: baño; cansancio: dormitorio; aburrimiento: salón.
- 0 es necesidad satisfecha y 100 es necesidad máxima.
- Las necesidades crecen con el tiempo; se reducen automáticamente en la habitación adecuada.
- Ollama decide la habitación; A* decide la ruta y JavaScript mueve el personaje.

## Notas

- La IA puede elegir decisiones poco óptimas: es un experimento de comportamiento, no un planificador determinista.
- Flask escucha únicamente en localhost. No expongas el servidor de desarrollo directamente a Internet.
- Las rutas usan una cuadrícula de 8 px; los muebles bloquean el paso.
