# JOCARSA Notificaciones

Sube el contenido de esta carpeta al DocumentRoot de https://notificaciones.jocarsa.com.
Requisitos: PHP 8.1+, pdo_sqlite, mbstring, HTTPS, Apache con AllowOverride para .htaccess.

Asegúrate de que `data/` es escribible por el usuario de PHP y no accesible desde HTTP. Idealmente, mueve DB_FILE a una carpeta fuera del DocumentRoot.

Primer inicio: usuario `jocarsa`, contraseña `jocarsa`. Cambia la contraseña inmediatamente mediante la API (ejemplo siguiente). El usuario inicial se crea solo si la tabla de usuarios está vacía.

Login:
```bash
curl -s https://notificaciones.jocarsa.com/api.php -H 'Content-Type: application/json' -d '{"accion":"login","usuario":"jocarsa","password":"jocarsa"}'
```
Guarda el token de la respuesta en una variable de shell, sin compartirlo.

Enviar:
```bash
curl -X POST https://notificaciones.jocarsa.com/api.php -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"accion":"enviar","titulo":"Aviso","descripcion":"Mensaje de prueba","icono":"📩"}'
```
Cambiar contraseña:
```bash
curl -X POST https://notificaciones.jocarsa.com/api.php -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"accion":"cambiar_password","actual":"jocarsa","nueva":"una-clave-segura-de-16-caracteres"}'
```
La modificación de contraseña invalida las sesiones existentes.

Nota: la API envía notificaciones a la cuenta autenticada, no a terceros. La interfaz consulta cada 15 segundos mientras está abierta; no hay push del sistema operativo. Los enlaces Inicio/Perfil son marcadores para futuras pantallas.

Seguridad: no expongas el token ni lo incluyas en repositorios. LocalStorage persiste entre sesiones pero es accesible a JavaScript del mismo origen; para mayor protección considera cookies HttpOnly y CSP estricta. Añade limitación de intentos de login en servidor antes de exponerlo públicamente.
