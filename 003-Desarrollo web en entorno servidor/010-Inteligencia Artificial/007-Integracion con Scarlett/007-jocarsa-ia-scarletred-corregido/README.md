# jocarsa | ia + administración ScarletRed

La ÚNICA base de datos es `data/ialocal.db`, que debes copiar desde la aplicación original de IA. El ZIP no incluye datos ni crea otra base de datos.

- `public/index.html`: chat de IA original.
- `public/servidor.php`: usa `../data/ialocal.db`.
- `admin/index.php`: panel ScarletRed adaptado a usuarios, conversaciones y mensajes.
- `crear_admin.php`: ejecutar una sola vez desde CLI `php crear_admin.php admin 'contraseña-segura'`; añade únicamente la columna `rol` a `usuarios` si falta y crea o promociona al administrador.

No se importan las tablas empresariales de ejemplo. Haz copia de seguridad de `data/ialocal.db` antes de instalar. Requiere PHP con PDO SQLite y servidor Ollama para el chat.
