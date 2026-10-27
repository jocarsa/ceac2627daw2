<?php

$db = new PDO("sqlite:../red.db");

$resultado = $db->query("SELECT * FROM publicaciones LIMIT 10");

$publicaciones = [];
while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
    $publicaciones[] = $fila;
}

echo json_encode($publicaciones);

?>