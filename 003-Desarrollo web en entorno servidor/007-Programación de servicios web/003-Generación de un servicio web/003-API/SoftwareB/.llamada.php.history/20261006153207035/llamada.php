<?php

$curl = curl_init("https://example.com");

curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($curl);

curl_close($curl);

echo $response;
?>