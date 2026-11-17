# 004-fusion — proyecto unificado

Se han combinado los códigos incluidos en los dos informes aportados. Ambos informes describen prácticamente el mismo árbol de proyecto; uno documenta `data/empresa.db` y el otro `data/ialocal.db`.

## Bases de datos

Copia **tus archivos SQLite reales**, con sus registros, a:

- `data/empresa.db` — utilizada por `admin/`
- `data/ialocal.db` — utilizada por `public/`

No se incluyen las bases reales: los documentos aportados contienen únicamente esquemas, no los archivos SQLite ni sus datos. **No se crea una base vacía que pueda confundirse con la original.**

Rutas actualizadas:
- `admin/config.php` apunta a `../data/empresa.db`.
- `public/servidor.php` apunta a `../data/ialocal.db`.

## Uso

Publica el proyecto en PHP con extensiones `pdo_sqlite` y `sqlite3`. Accede a `admin/index.php` y `public/index.html`. Configura Ollama según `public/servidor.php`. Concede a PHP permisos de lectura/escritura sobre las bases y su directorio para que SQLite pueda crear archivos WAL/journal.

**Seguridad:** mantén `data/` fuera del DocumentRoot del servidor web. Si el DocumentRoot es la raíz del proyecto, deniega explícitamente el acceso HTTP a `data/`. El panel administrativo original usa MD5 para validar contraseñas y operaciones de borrado por GET: conviene migrarlo a `password_hash/password_verify` y POST+CSRF antes de producción. No se ha alterado el esquema de usuarios ni sus credenciales en esta fusión.

**Alcance:** se unifica la distribución y centralización de bases de datos; los dos módulos mantienen sus sistemas de login y sus bases independientes.
