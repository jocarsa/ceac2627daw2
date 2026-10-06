Hola
<?php

  $curl = curl_init("../SoftwareA/api.php");
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  $respuesta = curl_exec($curl);
  curl_close($curl);
  echo $respuesta;
?>
Adios