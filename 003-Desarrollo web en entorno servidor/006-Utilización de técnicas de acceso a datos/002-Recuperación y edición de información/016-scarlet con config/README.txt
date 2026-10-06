ScarletRed MVC + configuración dinámica

Estructura:
- config.php: configuración central (nombre, logo, subtítulo, color y base de datos).
- leeconfiguracion.php: expone la configuración visual como JSON.
- Clases/modelo.php: JocarsaModelo, acceso a datos y CRUD.
- Clases/controlador.php: JocarsaControlador, login, sesión y acciones CRUD.
- Clases/vista.php: JocarsaVista, generación de interfaz.
- index.php: punto de entrada y composición MVC.
- login.php / matarsesion.php: endpoints de sesión que reutilizan modelo/controlador.

Para cambiar la identidad visual basta editar config.php.
Para usar los datos reales, coloca empresa.db en la raíz del proyecto o cambia 'basededatos' en config.php.
