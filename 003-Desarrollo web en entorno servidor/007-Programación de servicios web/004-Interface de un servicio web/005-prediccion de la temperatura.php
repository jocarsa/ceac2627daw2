<?php

$curl = curl_init("https://www.aemet.es/xml/municipios/localidad_46250.xml");

curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$respuesta = curl_exec($curl);

curl_close($curl);

$xml = simplexml_load_string($respuesta);

// Recorremos todos los días
foreach($xml->prediccion->dia as $dia){

    echo "Fecha: " . $dia["fecha"] . "<br>";

    echo "Temperatura máxima: "
        . $dia->temperatura->maxima
        . " ºC<br>";

    echo "Temperatura mínima: "
        . $dia->temperatura->minima
        . " ºC<br>";

    echo "<hr>";
}

?>