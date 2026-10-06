<?php

$archivo = fopen("datos.csv", "r");
$conjunto = [];
while (($fila = fgetcsv($archivo)) !== false) {
    $conjunto[] = $fila;
}
var_dump($conjunto);

fclose($archivo);

?>