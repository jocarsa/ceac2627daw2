# jocarsa fusion — base de datos única

Los dos módulos usan **exclusivamente** `data/ialocal.db`. Se crean automáticamente las tablas que falten, sin borrar las existentes. `empresa.db` ya no se utiliza.

## Instalación
1. Copia la carpeta al servidor Apache con PHP + pdo_sqlite + curl.
2. Si ya tienes `ialocal.db`, copia el archivo existente a `data/ialocal.db` **antes** del primer acceso. Haz una copia de seguridad.
3. Asegura permisos de escritura de PHP en `data/` y el archivo SQLite.
4. Crea un administrador desde terminal: `php crear_admin.php admin 'UnaClaveLargaYUnica123!'` (elige tu propia contraseña). Borra `crear_admin.php` después.
5. Accede a `admin/index.php` o `public/index.html`.

La autenticación de ambos módulos usa la misma tabla `usuarios`, con hashes `password_hash`. Solo `rol=admin` entra al panel. Los usuarios registrados en la IA tienen rol `usuario`. El panel gestiona tablas empresariales y no permite editar credenciales de usuario mediante el CRUD.

**Datos anteriores:** la documentación fuente no incluye los registros de `empresa.db`. Se crean sus tablas vacías; para conservar datos empresariales antiguos hay que migrarlos desde una copia de esa base. Las contraseñas antiguas en MD5 no se admiten: deben restablecerse.

**Seguridad:** evita exponer `data/` por HTTP. `.htaccess` protege en Apache si AllowOverride lo permite; lo ideal es denegar el directorio en el VirtualHost o mover el almacenamiento fuera de DocumentRoot. El CRUD heredado conserva eliminación por GET; úsalo solo en entorno de desarrollo hasta implementar CSRF y eliminación POST.
