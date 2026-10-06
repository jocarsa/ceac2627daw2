<?php

$curl = curl_init("https://www.aemet.es/xml/municipios/localidad_46250.xml");
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$respuesta = curl_exec($curl);
curl_close($curl);

// Convertimos el texto XML en un objeto SimpleXML
$xml = simplexml_load_string($respuesta);

// Acceder a propiedades
echo "Municipio: " . $xml->nombre . "<br>";
echo "Provincia: " . $xml->provincia . "<br>";

// Ver todo el objeto para descubrir su estructura
echo "<pre>";
print_r($xml);
echo "</pre>";

?>