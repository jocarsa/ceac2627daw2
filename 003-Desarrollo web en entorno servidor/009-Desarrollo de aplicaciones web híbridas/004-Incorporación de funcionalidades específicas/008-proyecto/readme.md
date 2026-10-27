# jocarsa | red

Proyecto PHP 8 + SQLite + JavaScript sin dependencias. Conserva el scroll infinito en ambas direcciones, con hasta 30 publicaciones montadas.

## Instalación sobre la base de datos existente

1. Copia `front/` y `migraciones/` sobre el proyecto existente **sin reemplazar `red.db`**.
2. Haz una copia de seguridad de `red.db`.
3. Desde la raíz del proyecto ejecuta:

   `sqlite3 red.db < migraciones/001_comentarios.sql`

4. Abre `front/index.html` desde Apache/PHP. Comprueba que PHP tenga `pdo_sqlite` habilitado y permisos de escritura sobre `red.db` y su directorio.

La migración es idempotente. `red.db` no se incluye porque el archivo recibido es documentación del proyecto, no una copia de la base de datos.

## Acceso

El login usa el campo `usuario` de `personas`. Admite contraseñas PHP `password_hash` y, para mantener la compatibilidad con datos de demostración antiguos, también texto plano. Conviene migrar las contraseñas de demostración a hashes antes de publicar el sitio. Las sesiones PHP restringen todos los endpoints de datos.

## Funcionalidad

- Perfil y buscador en la columna izquierda.
- Directorio de usuarios y botón Conectar.
- Las conexiones se interpretan como bidireccionales, aunque la tabla registra origen y destino. Una conexión nueva es inmediata, sin solicitud de aceptación.
- Feed del usuario y de las personas conectadas, con autor y fecha.
- Comentarios por publicación, creados por usuarios autenticados y visibles solo si la publicación pertenece al feed permitido.
- Scroll bidireccional con descarga de elementos DOM lejanos.

## Nota

No se adjuntó el archivo binario `red.db`, por lo que la migración debe ejecutarse sobre la base de datos original en el servidor.
