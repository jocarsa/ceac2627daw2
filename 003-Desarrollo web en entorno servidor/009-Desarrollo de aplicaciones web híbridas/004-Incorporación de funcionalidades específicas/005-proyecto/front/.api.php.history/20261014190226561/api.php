<?php

$db = new PDO("sqlite:../red.db");

$resultado = $db->query("SELECT * FROM publicaciones LIMIT 10");

$publicaciones = [];
while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
    echo $fila["nombre"] . " ";
    echo $fila["apellidos"] . "<br>";
}

?>