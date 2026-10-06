<?php

  // Inicializo la conexión
  $curl = curl_init(
    "http://localhost/ceac2627daw2/003-Desarrollo%20web%20en%20entorno%20servidor/007-Programaci%c3%b3n%20de%20servicios%20web/002-Est%c3%a1ndares%20y%20arquitecturas%20actuales.%20Formatos%20de%20intercambio%20de%20datos/002-API/SoftwareA/api.php"
  );

  // Quiero que me devuelva la respuesta
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

  // Envío la API Key
  curl_setopt($curl, CURLOPT_HTTPHEADER, [
    "X-API-Key: jocarsa_123456789_segura"
  ]);

  // Ejecuto la petición
  $respuesta = curl_exec($curl);

  // Cierro la conexión
  curl_close($curl);

  // Muestro la respuesta
  echo $respuesta;

?>