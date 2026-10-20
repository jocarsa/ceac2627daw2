<?php

$db = new PDO("sqlite:../red.db");

$resultado = $db->query("SELECT * FROM publicaciones LIMIT 10");

// Recorrer los resultados
while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
    echo $fila["nombre"] . " ";
    echo $fila["apellidos"] . "<br>";
}

?>