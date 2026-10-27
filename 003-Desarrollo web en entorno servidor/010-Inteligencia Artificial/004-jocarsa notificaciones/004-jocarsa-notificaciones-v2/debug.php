<?php

header("Content-Type: application/json");

$authorization =
    $_SERVER["HTTP_AUTHORIZATION"]
    ?? $_SERVER["REDIRECT_HTTP_AUTHORIZATION"]
    ?? null;

echo json_encode([
    "authorization_recibida" => !empty($authorization),
    "tipo" => $authorization
        ? explode(" ", $authorization)[0]
        : null
]);