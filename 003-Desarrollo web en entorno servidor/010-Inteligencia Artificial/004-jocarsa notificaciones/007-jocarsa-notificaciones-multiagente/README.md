# JOCARSA | Notificaciones multiagente

Sustituye `api.php`, `config.php`, `index.php` de V3 conservando `data/notificaciones.sqlite`. El esquema se amplía automáticamente. Requiere PHP 8.1+, PDO SQLite, mbstring.

Ejecuta el agente `agente_practicas_damdaw.py` con las variables IMAP_SERVER, IMAP_USER, IMAP_PASSWORD y NOTIFICACIONES_PASSWORD. La API mantiene el login y cabecera `X-Session-Token` de V3.

Enviar POST JSON: `{"accion":"enviar","agente":"practicas-damdaw","agente_nombre":"Prácticas DAMDAW","titulo":"Ejemplo","descripcion":"Detalle completo","icono":"🎓"}`.

Consultar GET `api.php?accion=agentes`, `api.php?accion=listar`, o `api.php?accion=listar&agente=practicas-damdaw`.

**Seguridad:** el nombre/clave del agente son identidad declarada, no credenciales independientes. El token del usuario autentica la petición. Para aislar agentes entre sí se necesitarán claves propias por agente. Cambia la contraseña inicial `jocarsa` antes de producción.
