<?php

// ============================================
// CONFIGURACIÓN
// ============================================

$API_KEY_CORRECTA = "jocarsa_123456789_segura";


// ============================================
// CABECERAS
// ============================================

header("Content-Type: application/json; charset=UTF-8");


// ============================================
// OBTENER API KEY
// ============================================

$api_key = $_SERVER["HTTP_X_API_KEY"] ?? "";


// ============================================
// COMPROBAR API KEY
// ============================================

if ($api_key !== $API_KEY_CORRECTA) {

    http_response_code(401);

    echo json_encode([
        "error" => true,
        "mensaje" => "API Key incorrecta o no proporcionada"
    ]);

    exit;
}


// ============================================
// RESPUESTA DE LA API
// ============================================

http_response_code(200);

echo json_encode([
    "nombre" => "Jose Vicente",
    "apellidos" => "Carratala Sanchis",
    "email" => "info@josevicentecarratala.com"
], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

?>