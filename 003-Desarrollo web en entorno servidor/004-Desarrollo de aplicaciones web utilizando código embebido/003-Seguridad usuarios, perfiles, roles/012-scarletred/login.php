<?php
session_start();
if($_SERVER['REQUEST_METHOD'] !== 'POST'){ header("Location:index.php"); exit(); }
$db = new SQLite3('empresa.db');
$stmt = $db->prepare("SELECT * FROM usuarios WHERE usuario=:usuario AND contrasena=:contrasena");
$stmt->bindValue(':usuario', $_POST['usuario'] ?? '', SQLITE3_TEXT);
$stmt->bindValue(':contrasena', $_POST['contrasena'] ?? '', SQLITE3_TEXT);
$result = $stmt->execute();
if($fila = $result->fetchArray(SQLITE3_ASSOC)){
    session_regenerate_id(true);
    $_SESSION['llave'] = "jocarsa";
    $_SESSION['rol'] = $fila['rol'];
    $_SESSION['nombre'] = $fila['nombre'];
    header("Location:index.php");
}else{
    header("Location:index.php?error=1");
}
$db->close();
exit();
