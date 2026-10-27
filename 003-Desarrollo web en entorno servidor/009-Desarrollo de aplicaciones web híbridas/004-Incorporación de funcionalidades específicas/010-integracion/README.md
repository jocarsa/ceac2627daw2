# jocarsa | red

Actualización del frontend público y control de privacidad de perfiles. Mantiene el panel administrativo existente.

## Instalación
1. Hacer copia de seguridad de `red.db`.
2. Copiar `front/` y `admin/index.php` sobre el proyecto existente, conservando `red.db`.
3. Ejecutar **una sola vez** la migración: `sqlite3 red.db < migraciones/002_perfiles_publicos.sql` (o desde PHP/PDO SQLite).
4. Abrir `/front/index.html`.

La migración deja todos los perfiles existentes como privados (0). Desde el panel admin o desde el perfil de cada usuario se puede habilitar perfil público (1). Los visitantes anónimos ven exclusivamente posts y comentarios correspondientes a publicaciones de autores públicos. Los usuarios autenticados conservan el feed basado en conexiones. El control de acceso se aplica en la API PHP.

Este paquete se reconstruye desde el reporte Markdown adjunto y **no contiene la base de datos original**.

## Registro público de nuevos usuarios

El formulario «Únete a la comunidad» crea cuentas en `personas` mediante `front/api.php?accion=registro`. Requiere haber aplicado la migración `002_perfiles_publicos.sql`. Las contraseñas se almacenan con `password_hash`, se comprueba la unicidad de usuario y correo, y se inicia sesión tras registrarse. El perfil es privado por defecto; puede hacerse público marcando la casilla de registro o desde el perfil. No se incluye `red.db` en el ZIP.

Para un despliegue abierto a Internet, añadir verificación de correo electrónico, limitación de intentos por IP y protección antispam/CAPTCHA antes de permitir registros masivos.
