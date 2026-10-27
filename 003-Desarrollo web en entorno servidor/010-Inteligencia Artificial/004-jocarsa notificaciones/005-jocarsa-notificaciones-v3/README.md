# JOCARSA Notificaciones V3

## Instalación

Copiar el contenido al directorio web de `https://notificaciones.jocarsa.com`. PHP 8.1+, PDO SQLite y mbstring requeridos. La carpeta `data` debe ser escribible por el usuario PHP/Apache. La base de datos se crea automáticamente al entrar en `api.php`.

**Usuario inicial:** jocarsa
**Contraseña inicial:** jocarsa

Cambiar la contraseña inmediatamente desde Perfil. En producción habilitar HTTPS, limitar intentos de login mediante servidor/proxy y proteger backups de SQLite. Los tokens se guardan como hash SHA-256 en SQLite y el token original en localStorage (no almacenar la contraseña). Al usar localStorage, prevenir XSS y evitar scripts de terceros no confiables.

## API

Todas las llamadas, excepto login, requieren `X-Session-Token: TOKEN`. No se usa Authorization, por compatibilidad con Apache.

### Login

```bash
curl -X POST https://notificaciones.jocarsa.com/api.php -H 'Content-Type: application/json' -d '{"accion":"login","usuario":"jocarsa","password":"jocarsa"}'
```

Guardar el campo `token` de la respuesta.

### Enviar

```bash
curl -X POST https://notificaciones.jocarsa.com/api.php \
  -H 'Content-Type: application/json' \
  -H 'X-Session-Token: TU_TOKEN' \
  -d '{"accion":"enviar","titulo":"Nuevo mensaje","descripcion":"Notificación de prueba","icono":"📩"}'
```

### Listar

```bash
curl 'https://notificaciones.jocarsa.com/api.php?accion=listar' -H 'X-Session-Token: TU_TOKEN'
```

### Marcar leída

```json
{"accion":"leer","id":1}
```

### Cambiar contraseña

```json
{"accion":"cambiar_password","actual":"jocarsa","nueva":"una-clave-segura-de-12-o-mas"}
```

### Cerrar sesión

```json
{"accion":"logout"}
```

## Migraciones

Esta V3 utiliza el esquema propio de `config.php`. Si tienes una base anterior con tablas diferentes, haz copia de seguridad y usa una base nueva, o migra los datos antes de desplegar. No borres una base de datos con notificaciones que quieras conservar.

## Notas

- No hay Web Push con la aplicación cerrada; el navegador consulta cada 15 segundos mientras la página está visible.
- Los botones Inicio y Perfil son acciones básicas; Perfil permite cambiar contraseña.
- El endpoint `enviar` crea notificaciones para el usuario autenticado.
- Las fechas SQLite se almacenan en UTC.
