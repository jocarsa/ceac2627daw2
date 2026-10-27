<?php
declare(strict_types=1);
const DB_FILE = __DIR__ . '/data/notificaciones.sqlite';
function db(): PDO {
    static $pdo = null;
    if ($pdo) return $pdo;
    if (!is_dir(dirname(DB_FILE))) mkdir(dirname(DB_FILE), 0700, true);
    $pdo = new PDO('sqlite:' . DB_FILE);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    $pdo->exec('PRAGMA foreign_keys=ON');
    $pdo->exec('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)');
    $pdo->exec('CREATE TABLE IF NOT EXISTS sesiones (token_hash TEXT PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), expira INTEGER NOT NULL)');
    $pdo->exec('CREATE TABLE IF NOT EXISTS notificaciones (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), titulo TEXT NOT NULL, descripcion TEXT NOT NULL, icono TEXT NOT NULL DEFAULT "🔔", fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, leida INTEGER NOT NULL DEFAULT 0)');
    $count = (int)$pdo->query('SELECT COUNT(*) FROM usuarios')->fetchColumn();
    if ($count === 0) {
        $stmt = $pdo->prepare('INSERT INTO usuarios(usuario,password_hash) VALUES (?,?)');
        $stmt->execute(['jocarsa', password_hash('jocarsa', PASSWORD_DEFAULT)]);
    }
    return $pdo;
}
function respond(array $data, int $status = 200): never {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}
function currentUser(PDO $db): array {
    $header = $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '';
    if (!preg_match('/^Bearer ([a-f0-9]{64})$/i', $header, $m)) respond(['error'=>'No autorizado'],401);
    $stmt = $db->prepare('SELECT u.id,u.usuario FROM sesiones s JOIN usuarios u ON u.id=s.usuario_id WHERE s.token_hash=? AND s.expira>?');
    $stmt->execute([hash('sha256', $m[1]),time()]);
    $user = $stmt->fetch();
    if (!$user) respond(['error'=>'Sesión caducada'],401);
    return $user;
}
