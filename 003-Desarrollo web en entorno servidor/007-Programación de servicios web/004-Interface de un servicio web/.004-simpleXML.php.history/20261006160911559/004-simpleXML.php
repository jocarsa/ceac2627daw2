<?php

$curl = curl_init("https://www.aemet.es/xml/municipios/localidad_46250.xml");
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$respuesta = curl_exec($curl);
curl_close($curl);

$xml = simplexml_load_string($respuesta);

// Acceder a propiedades
//echo "Provincia: " . $xml->provincia . "<br>";
echo $xml->prediccion->dia."<br>";


?>