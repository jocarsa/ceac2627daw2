# jocarsa | red + ScarletRed

Integración del frontend original con backoffice ScarletRed en PHP/SQLite. El administrador gestiona las cinco entidades originales directamente en `red.db`; no hay sincronización ni copia CSV. Conserva el estilo de ScarletRed, CRUD, login administrativo, búsqueda, paginación y exportación CSV.

## Instalación

1. Copiar el contenido del ZIP a la carpeta del proyecto, **sin reemplazar el `red.db` real**. El ZIP no incluye una base de datos de demostración.
2. Verificar que existe `red.db` en la raíz y que PHP tiene PDO SQLite y mbstring.
3. Si falta la tabla de comentarios, aplicar `sqlite3 red.db < migraciones/001_comentarios.sql`.
4. Crear un administrador ejecutando `php admin/scripts/crear_admin.php admin jocarsa` (cambiar la contraseña en producción).
5. Abrir `/front/index.html` para la red y `/admin/index.php` para el backoffice.

## Consideraciones

- Los administradores se autentican en `admin_usuarios`, separada de `personas`.
- No se exponen contraseñas ni hashes en listados o exportaciones. Las contraseñas de usuarios editadas desde el panel se guardan con `password_hash`.
- Las claves foráneas de la base original se respetan; SQLite puede impedir eliminaciones con registros relacionados. El administrador deberá eliminar primero los registros dependientes cuando corresponda.
- La interfaz conserva la estructura y la hoja de estilos de ScarletRed, pero sustituye el motor CSV por un modelo SQLite.
- El ZIP se ha reconstruido a partir de los dos reportes Markdown, no de las carpetas originales.
