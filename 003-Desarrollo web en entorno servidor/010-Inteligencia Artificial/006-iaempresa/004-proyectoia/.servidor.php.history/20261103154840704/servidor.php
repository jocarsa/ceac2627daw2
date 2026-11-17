<?php
$datos = [
    "model" => "llama3.2:1b",
    "prompt" => $_GET['mensaje'],
    "stream" => false
];

$curl = curl_init("http://localhost:11434/api/generate");
curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($datos));
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$respuesta = json_decode(curl_exec($curl), true);
curl_close($curl);

echo $respuesta["response"];
?>
