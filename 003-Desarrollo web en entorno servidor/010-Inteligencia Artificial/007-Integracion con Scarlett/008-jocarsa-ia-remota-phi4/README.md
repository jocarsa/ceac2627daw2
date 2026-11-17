# jocarsa | ia + ScarletRed + Phi-4 remoto

Única base de datos: `data/ialocal.db`. Copia aquí tu SQLite original; no se incluye en el ZIP.

La aplicación `public/servidor.php` envía las preguntas a la API HTTPS `/daw/` y lee el campo JSON `respuesta`. Conserva el historial de conversaciones en SQLite.

**Configura la clave** en `config_ia_remota.php` (propiedad `token`) o preferiblemente mediante la variable de entorno `JOCARSA_IA_API_TOKEN` accesible a PHP/Apache. No pongas la clave en JavaScript ni en `public/`.

La API remota solo admite `mensaje`, por lo que se envían los últimos 12 mensajes en formato texto para conservar contexto. Comprueba que el servidor remoto acepta ese formato.

No se necesitan Ollama ni modelos locales en el servidor web. Se requiere extensión PHP cURL y acceso HTTPS al túnel. Si cambia la URL temporal de Cloudflare, actualiza `config_ia_remota.php`.

La clave compartida en el chat debe considerarse expuesta: se recomienda rotarla antes de publicar el proyecto.
