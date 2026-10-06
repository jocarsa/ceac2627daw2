<?php

include "JocarsaJSON.php";

$jocarsaJSON = new JocarsaJSON();


// ================================
// GUARDAR JSON
// ================================

$datos = [
    "nombre" => "Jose Vicente",
    "apellidos" => "Carratala",
    "profesion" => "Profesor",
    "tecnologias" => [
        "PHP",
        "Python",
        "JavaScript",
        "SQL"
    ]
];

$jocarsaJSON->guardarJSON("datos.json", $datos);


// ================================
// CARGAR JSON
// ================================

$datosCargados = $jocarsaJSON->cargarJSON("datos.json");

print_r($datosCargados);

?>