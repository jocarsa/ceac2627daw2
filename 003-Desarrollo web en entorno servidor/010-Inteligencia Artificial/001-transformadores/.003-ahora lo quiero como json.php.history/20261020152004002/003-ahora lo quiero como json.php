
<?php

$url = "http://localhost:11434/api/embed";

$datos = [
    "model" => "nomic-embed-text:latest",
    "input" => "perro"
];

$curl = curl_init($url);

curl_setopt_array($curl, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => [
        "Content-Type: application/json"
    ],
    CURLOPT_POSTFIELDS => json_encode($datos),
    CURLOPT_TIMEOUT => 120
]);

$respuesta = curl_exec($curl);

if ($respuesta === false) {
    die("Error cURL: " . curl_error($curl));
}

$codigo = curl_getinfo($curl, CURLINFO_HTTP_CODE);
curl_close($curl);

if ($codigo !== 200) {
    die("Error Ollama ($codigo): " . $respuesta);
}

$resultado = json_decode($respuesta, true);

$vector = $resultado["embeddings"][0];

echo json_encode($vector);

?>
