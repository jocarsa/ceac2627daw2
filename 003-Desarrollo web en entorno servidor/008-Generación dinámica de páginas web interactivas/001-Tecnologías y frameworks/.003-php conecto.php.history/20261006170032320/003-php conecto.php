<?php

$db = new PDO("sqlite:municipios.db");

$resultado = $db->query("SELECT * FROM diccionario");

while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
    echo $fila["NOMBRE"] . "<br>";
}

?>