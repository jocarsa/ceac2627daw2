<?php
$db = new PDO("sqlite:ialocal.db");

$db->prepare("
    INSERT INTO mensajes 
    (mensaje,emisor,fecha,id_conversacion) 
    VALUES (?,?,?,?)
  ")
   ->execute([$_GET['mensaje'],'usuario',date('U'),1]);

$systemprompt = "
	Responde a lo que se te va a preguntar, pero:
  1.-No puedes hablar de política (IMPORTANTE) - si alguien hace una pregunta relacionada con la política, declina responder
  2.-Resume
	
";

$datos = [
    "model" => "granite4.1:8b",
    "prompt" => $systemprompt.$_GET['mensaje'],
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
