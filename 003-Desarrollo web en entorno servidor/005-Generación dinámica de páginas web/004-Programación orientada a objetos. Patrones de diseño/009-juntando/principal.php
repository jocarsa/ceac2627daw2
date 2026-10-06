<?php

include "vista.php";
include "modelo.php";
include "controlador.php";

$clientes = JocarsaModelo::dameDatosEstatico(
    "clientes.db",
    "clientes"
);

$json = coseJSON($clientes);

$vista = new JocarsaVista($json);
$vista->pintaTabla();

?>