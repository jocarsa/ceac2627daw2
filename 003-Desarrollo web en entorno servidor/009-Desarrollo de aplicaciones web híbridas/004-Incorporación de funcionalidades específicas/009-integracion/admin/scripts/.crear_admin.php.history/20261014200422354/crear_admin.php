<?php

if (PHP_SAPI !== 'cli') {
    exit("Este script solo se ejecuta desde terminal.\n");
}

if ($argc < 3) {
    exit("Uso: php crear_admin.php usuario contraseña [nombre]\n");
}

$usuario = $argv[1];
$contrasena = $argv[2];
$nombre = $argv[3] ?? 'Administrador';

$ruta = dirname(__DIR__, 2) . '/red.db';

if (!is_file($ruta)) {
    exit("Error: No existe la base de datos: $ruta\n");
}

$db = new PDO('sqlite:' . $ruta);

$db->setAttribute(
    PDO::ATTR_ERRMODE,
    PDO::ERRMODE_EXCEPTION
);

$db->exec("
    CREATE TABLE IF NOT EXISTS admin_usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL UNIQUE,
        contrasena TEXT NOT NULL,
        nombre TEXT NOT NULL,
        rol TEXT NOT NULL DEFAULT 'admin'
    )
");

$hash = password_hash($contrasena, PASSWORD_DEFAULT);

$sql = "
    INSERT INTO admin_usuarios
        (usuario, contrasena, nombre, rol)
    VALUES
        (:usuario, :contrasena, :nombre, 'admin')
    ON CONFLICT(usuario) DO UPDATE SET
        contrasena = excluded.contrasena,
        nombre = excluded.nombre,
        rol = excluded.rol
";

$stmt = $db->prepare($sql);

$stmt->execute([
    ':usuario' => $usuario,
    ':contrasena' => $hash,
    ':nombre' => $nombre
]);

echo "Administrador creado o actualizado correctamente.\n";
echo "Usuario: $usuario\n";
echo "Nombre: $nombre\n";