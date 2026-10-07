<?php

$db = new PDO("sqlite:database.db");

$resultado = $db->query("SELECT * FROM usuarios");

while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
    echo $fila["id"] . " - ";
    echo $fila["nombre"] . " - ";
    echo $fila["email"] . "<br>";
}

?>