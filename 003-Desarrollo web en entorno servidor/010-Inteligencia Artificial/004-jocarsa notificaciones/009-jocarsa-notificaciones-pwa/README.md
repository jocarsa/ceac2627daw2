# JOCARSA Notificaciones PWA + Web Push

## Instalación

1. Copia los archivos del ZIP a la raíz HTTPS de `notificaciones.jocarsa.com`, **sin borrar `data/notificaciones.sqlite`**. Conserva los permisos de escritura de `data`.
2. En el servidor ejecuta `composer install --no-dev --optimize-autoloader` (PHP 8.2+ recomendado para `minishlink/web-push` v9).
3. Genera una pareja VAPID una sola vez con `php -r 'require "vendor/autoload.php"; print_r(Minishlink\WebPush\VAPID::createVapidKeys());'`.
4. Configura **en el entorno PHP del servidor web** `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY` y `VAPID_SUBJECT=mailto:tu-correo@dominio.com`. No publiques la clave privada ni la incluyas en JavaScript. Comprueba que PHP-FPM/Apache recibe las variables (no basta con exportarlas en tu terminal).
5. Abre la web con HTTPS, inicia sesión y pulsa **Activar notificaciones en este dispositivo**. Instala la PWA desde el menú del navegador. En iOS, añádela a pantalla de inicio y abre la aplicación instalada para activar las notificaciones (iOS 16.4+).

## Funcionamiento

- `api.php` conserva las acciones de la versión multiagente. `enviar` guarda la notificación y, a continuación, intenta enviar un Web Push a cada dispositivo suscrito del usuario.
- `push_config`, `push_suscribir` y `push_cancelar` requieren sesión excepto `login` como antes. Las suscripciones se guardan en SQLite.
- `sw.js` muestra notificaciones incluso con la PWA cerrada, si el navegador/sistema admite Web Push, la suscripción sigue activa y el dispositivo tiene conectividad. La entrega no está garantizada por el sistema operativo.
- Sin Composer/VAPID, la app y los avisos internos siguen funcionando, pero **no habrá notificaciones push con la app cerrada**.
- El script Python `agente_practicas_damdaw.py` se mantiene sin cambios.
- El icono incluido es genérico y puedes sustituirlo por el logotipo oficial.

## Seguridad

Cambia la contraseña inicial `jocarsa` inmediatamente. La API existente sigue autenticando los agentes mediante sesión de usuario: no proporciona todavía credenciales independientes por agente. Mantén `data/` fuera del acceso público (o protegido con `.htaccess`), limita intentos de login y protege las claves VAPID. No caches respuestas autenticadas de la API.
