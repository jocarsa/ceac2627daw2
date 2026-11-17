ScarletRed MVC - edición JocarsaCSV

1. Ya no usa SQLite/PDO. Cada tabla es datos/empresa/<tabla>.csv.
2. Ejecuta una vez importar_ejemplo.php para crear datos de demostración.
3. Acceso: admin / admin123 (o ventas / ventas123).
4. El controlador y la vista conservan la API del modelo original.
5. Las claves primarias se declaran en config.php porque CSV no dispone de esquema.
