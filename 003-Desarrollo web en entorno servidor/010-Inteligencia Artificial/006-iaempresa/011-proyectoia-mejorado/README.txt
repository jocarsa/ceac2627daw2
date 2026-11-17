JOCARSA IA - Instalación

1. Copia index.html, estilo.css, comportamiento.js y servidor.php a la carpeta de tu proyecto.
2. Conserva tu archivo ialocal.db original en esa carpeta: no se incluye en el ZIP porque el informe adjunto solo contiene su esquema, no los datos.
3. Da permisos de escritura al usuario de PHP sobre ialocal.db y su directorio (SQLite crea archivos auxiliares).
4. Activa las extensiones PHP pdo_sqlite, curl y mbstring.
5. Inicia Ollama y descarga el modelo configurado en servidor.php (granite4.1:8b), o cambia el nombre por uno instalado.
6. Accede a index.html mediante Apache/PHP (no mediante file://).

Seguridad: usuarios nuevos usan password_hash. Si ya existían usuarios con contraseñas en texto plano, no se migran automáticamente: hay que restablecer sus contraseñas. El registro es público; restringe su acceso si es un entorno privado. No publiques ialocal.db: usa una regla de denegación del servidor o muévelo fuera del directorio público y ajusta su ruta en PHP.

DISEÑO JOCARSA UI
Se incluye CSS original de jocarsa-iu y una capa jocarsa-adaptacion.css para adaptar el chat a su identidad visual (color HSL, chaflanes, paneles y tipografia).

Identidad: jocarsa | ia; color corporativo LightSkyBlue (#87CEFA); logo y favicon https://static.jocarsa.com/logos/lightskyblue.svg
