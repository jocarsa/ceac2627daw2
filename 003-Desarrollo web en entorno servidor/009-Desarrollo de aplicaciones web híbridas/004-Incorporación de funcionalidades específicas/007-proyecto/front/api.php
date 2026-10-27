<?php
header('Content-Type: application/json; charset=utf-8');
try {
    $db = new PDO('sqlite:' . __DIR__ . '/../red.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $offset = max(0, (int)($_GET['offset'] ?? 0));
    $limite = min(50, max(1, (int)($_GET['limite'] ?? 10)));
    $consulta = $db->prepare('SELECT id, id_persona, fecha, contenidos FROM publicaciones ORDER BY fecha DESC, id DESC LIMIT :limite OFFSET :offset');
    $consulta->bindValue(':limite', $limite, PDO::PARAM_INT);
    $consulta->bindValue(':offset', $offset, PDO::PARAM_INT);
    $consulta->execute();
    echo json_encode($consulta->fetchAll(PDO::FETCH_ASSOC), JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(['error' => 'No se pudieron recuperar las publicaciones']);
}
