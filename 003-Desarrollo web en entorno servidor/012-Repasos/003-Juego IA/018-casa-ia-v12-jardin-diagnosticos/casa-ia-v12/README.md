# Casa IA v12 · Barrio de cuatro casas

Cuatro casas dentro de un mismo mundo, con jardín compartido y transitable.
Cada casa tiene dos puertas exteriores (norte y sur, de dos baldosas).
Ocho personajes (dos por casa) conservan su `home` incluso cuando pasean fuera.
Solo pueden satisfacer sed, pipí y cansancio en **su propia** cocina, baño y dormitorio.
El aburrimiento se reduce en su salón o en cualquier punto del jardín.

## Ejecutar

```bash
ollama pull qwen2.5:7b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir http://127.0.0.1:5000

## Diagnóstico de movimiento

El navegador envía automáticamente cada **20 segundos** un JSON al servidor,
que lo guarda en `diagnosticos/diagnostico-AAAA...json`. Incluye muestras de
posición cada segundo (últimos 120 segundos), decisiones, bloqueos, destinos,
identificadores de casa, necesidades y arrastres. El botón «Exportar diagnóstico
JSON» descarga una copia inmediata para compartir. No registra cada fotograma,
para evitar ficheros gigantes.

El intervalo de reevaluación de Ollama es independiente de los 20 segundos de
exportación y se ajusta con el control superior.

Las rutas ignoran temporalmente a los otros personajes al planificarse; en
movimiento se comprueba la ocupación y se replanifica si es necesario.
