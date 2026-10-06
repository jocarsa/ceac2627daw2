<?php
	$fecha = date('Y').date('m').date('d').date('H').date('i').date('s');
  $curl = curl_init("https://www.aemet.es/xml/municipios/localidad_46250.xml");
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  $respuesta = curl_exec($curl);
  curl_close($curl);
  echo $respuesta;
  $archivo = fopen("prediccion".$fecha.".xml",'w');
  fwrite($archivo,$respuesta);
  fclose($archivo);
?>
