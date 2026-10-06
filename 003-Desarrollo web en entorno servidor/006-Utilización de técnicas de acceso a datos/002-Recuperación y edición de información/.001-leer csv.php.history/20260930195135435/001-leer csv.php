<?php

$archivo = fopen("datos.csv", "r");

while (($fila = fgetcsv($archivo)) !== false) {
    print_r($fila);
}

fclose($archivo);

?>