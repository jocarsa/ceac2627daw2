<?php

  $curl = curl_init("../SoftwareA/api.php");
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  $response = curl_exec($curl);
  curl_close($curl);
  echo $response;
?>