<?php
	$fecha = date('Y').date('m').date('d').date('H').date('i').date('s');
  $curl = curl_init("https://www.aemet.es/xml/municipios/localidad_46250.xml");
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  $respuesta = curl_exec($curl);
  curl_close($curl);
  echo $respuesta;
  $archivo = fopen("/var/www/html/ceac2627daw2/003-Desarrollo%20web%20en%20entorno%20servidor/007-Programación%20de%20servicios%20web/005-Consumo%20de%20un%20servicio%20web.%20Herramientas%20de%20prueba/predicciones/prediccion".$fecha.".xml",'w');
  fwrite($archivo,$respuesta);
  fclose($archivo);
?>
