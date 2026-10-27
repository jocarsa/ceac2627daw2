<?php

$db = new PDO("sqlite:../red.db");

// Ejecutar consulta
$resultado = $db->query("SELECT * FROM personas");

// Recorrer los resultados
while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
    echo $fila["nombre"] . " ";
    echo $fila["apellidos"] . "<br>";
}

?>