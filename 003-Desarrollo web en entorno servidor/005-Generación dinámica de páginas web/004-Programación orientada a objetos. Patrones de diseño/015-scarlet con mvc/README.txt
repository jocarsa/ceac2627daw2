ScarletRed MVC

Reestructuración del proyecto ScarletRed usando tres clases Jocarsa:
- modelo.php       -> JocarsaModelo: PDO/SQLite, esquema, CRUD, login y roles.
- controlador.php  -> JocarsaControlador: sesión, acciones, permisos y coordinación.
- vista.php        -> JocarsaVista: todo el HTML de login, panel, tabla y formulario.
- index.php        -> composición de MVC; no contiene consultas SQL.

IMPORTANTE:
Copia el empresa.db ORIGINAL de ScarletRed a esta carpeta. El reporte suministrado documenta el esquema, pero no contiene los bytes/registros de la base de datos.

Se conserva:
- login por sesión
- roles y navegación por tablas
- CRUD dinámico
- detección automática de PK
- formulario alta/edición
- estilo ScarletRed existente

Mejoras estructurales:
- PDO en todo el modelo
- consultas parametrizadas para valores
- validación de identificadores SQL
- autorización de tabla contra las tablas permitidas del rol
- vista sin acceso directo a SQLite
