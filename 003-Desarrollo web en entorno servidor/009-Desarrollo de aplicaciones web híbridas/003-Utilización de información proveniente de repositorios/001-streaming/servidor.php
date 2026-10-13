<?php

$json = file_get_contents("repositorio/titulos.json");

$datos = json_decode($json, true);

$peliculas = array_slice($datos["peliculas"], 0, 10);

echo json_encode($peliculas);
?>
