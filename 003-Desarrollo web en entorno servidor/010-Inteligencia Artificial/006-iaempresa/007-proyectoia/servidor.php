<?php
$db = new PDO("sqlite:ialocal.db");

$id_conversacion = 1;
$mensaje = $_GET['mensaje'];

// Guardar mensaje del usuario
$db->prepare("
    INSERT INTO mensajes
    (mensaje,emisor,fecha,id_conversacion)
    VALUES (?,?,?,?)
")->execute([$mensaje,'usuario',date('U'),$id_conversacion]);

// Recuperar los últimos 6 mensajes
// (5 anteriores + el mensaje actual)
$consulta = $db->prepare("
    SELECT mensaje, emisor
    FROM mensajes
    WHERE id_conversacion = ?
    ORDER BY rowid DESC
    LIMIT 6
");
$consulta->execute([$id_conversacion]);

$mensajes = array_reverse($consulta->fetchAll(PDO::FETCH_ASSOC));

// Prompt del sistema
$systemprompt = "
Responde a lo que se te va a preguntar, pero:
1.-No puedes hablar de política (IMPORTANTE).
Si alguien pregunta sobre política, declina responder.
2.-Resume.
";

// Construir contexto
$contexto = "";

foreach ($mensajes as $m) {
    $rol = $m['emisor'] == 'usuario' ? 'Usuario' : 'Asistente';
    $contexto .= $rol . ": " . $m['mensaje'] . "\n";
}

$contexto .= "Asistente: ";

// Enviar a Ollama
$datos = [
    "model" => "granite4.1:8b",
    "system" => $systemprompt,
    "prompt" => $contexto,
    "stream" => false
];

$curl = curl_init("http://localhost:11434/api/generate");

curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($datos));
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($curl, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);

$respuesta = json_decode(curl_exec($curl), true);

curl_close($curl);

// Guardar respuesta
$db->prepare("
    INSERT INTO mensajes
    (mensaje,emisor,fecha,id_conversacion)
    VALUES (?,?,?,?)
")->execute([
    $respuesta["response"],
    'ia',
    date('U'),
    $id_conversacion
]);

echo $respuesta["response"];
?>