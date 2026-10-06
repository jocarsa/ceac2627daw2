<?php

  // Inicializo la conexión
  $curl = curl_init(
    "http://localhost/ceac2627daw2/003-Desarrollo%20web%20en%20entorno%20servidor/007-Programaci%c3%b3n%20de%20servicios%20web/003-Generaci%c3%b3n%20de%20un%20servicio%20web/003-API/SoftwareA/api.php"
  );

  // Quiero que me devuelva la respuesta
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

  // Envío la API Key /////////// IMPORTANTE
  curl_setopt($curl, CURLOPT_HTTPHEADER, [
    "X-API-Key: jocarsa_123456789_seguraB"
  ]);

  // Ejecuto la petición
  $respuesta = curl_exec($curl);

  // Cierro la conexión
  curl_close($curl);

  // Muestro la respuesta
  echo $respuesta;

?>