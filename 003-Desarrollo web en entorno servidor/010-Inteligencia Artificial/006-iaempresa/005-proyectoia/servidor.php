<?php
$db = new PDO("sqlite:ialocal.db");

$db->prepare("
    INSERT INTO mensajes 
    (mensaje,emisor,fecha,id_conversacion) 
    VALUES (?,?,?,?)
  ")
   ->execute([$_GET['mensaje'],'usuario',date('U'),1]);
   
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
   
$db->prepare("
    INSERT INTO mensajes 
    (mensaje,emisor,fecha,id_conversacion) 
    VALUES (?,?,?,?)
  ")
   ->execute([$respuesta["response"],'ia',date('U'),1]);

echo $respuesta["response"];
?>
