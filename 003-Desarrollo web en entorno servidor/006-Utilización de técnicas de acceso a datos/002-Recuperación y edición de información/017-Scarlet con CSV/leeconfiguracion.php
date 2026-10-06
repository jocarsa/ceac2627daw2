<?php
require __DIR__ . '/config.php';
header('Content-Type: application/json; charset=utf-8');
echo json_encode([
    'nombre' => $config['nombre'],
    'logo' => $config['logo'],
    'subtitulo' => $config['subtitulo'],
    'color' => $config['color']
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);