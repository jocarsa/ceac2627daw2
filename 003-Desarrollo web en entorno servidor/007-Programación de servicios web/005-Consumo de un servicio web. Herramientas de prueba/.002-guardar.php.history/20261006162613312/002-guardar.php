<?php

$fecha = date('YmdHis');

$curl = curl_init("https://www.aemet.es/xml/municipios/localidad_46250.xml");
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$respuesta = curl_exec($curl);
curl_close($curl);

$archivo = fopen(
    __DIR__ . "/predicciones/prediccion" . $fecha . ".xml",
    "w"
);

fwrite($archivo, $respuesta);
fclose($archivo);

echo "Guardado: prediccion" . $fecha . ".xml\n";
?>