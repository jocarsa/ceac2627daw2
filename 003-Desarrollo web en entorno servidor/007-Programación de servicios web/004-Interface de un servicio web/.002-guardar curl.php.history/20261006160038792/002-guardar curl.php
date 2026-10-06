<?php
  $curl = curl_init("https://www.aemet.es/xml/municipios/localidad_46250.xml");
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  $respuesta = curl_exec($curl);
  curl_close($curl);
  echo $respuesta;
  $archivo = fopen("prediccion.xml")
?>
