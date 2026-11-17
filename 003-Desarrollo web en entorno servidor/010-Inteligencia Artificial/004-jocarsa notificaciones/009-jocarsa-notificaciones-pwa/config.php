<?php
declare(strict_types=1);
const DB_FILE = __DIR__ . '/data/notificaciones.sqlite';
const SESSION_DAYS = 30;
function db(): PDO {
    static $pdo = null;
    if ($pdo instanceof PDO) return $pdo;
    if (!is_dir(dirname(DB_FILE))) mkdir(dirname(DB_FILE), 0770, true);
    $pdo = new PDO('sqlite:' . DB_FILE);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    $pdo->exec('PRAGMA foreign_keys = ON');
    $pdo->exec('PRAGMA busy_timeout = 5000');
    $pdo->exec('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)');
    $pdo->exec('CREATE TABLE IF NOT EXISTS sesiones (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, token_hash TEXT NOT NULL UNIQUE, expira INTEGER NOT NULL, creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE)');
    $pdo->exec("CREATE TABLE IF NOT EXISTS notificaciones (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, titulo TEXT NOT NULL, descripcion TEXT NOT NULL, icono TEXT NOT NULL DEFAULT '🔔', leida INTEGER NOT NULL DEFAULT 0, creada TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE)");
    $pdo->exec('CREATE TABLE IF NOT EXISTS push_suscripciones (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, endpoint TEXT NOT NULL UNIQUE, p256dh TEXT NOT NULL, auth TEXT NOT NULL, creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE)');
    $pdo->exec('CREATE TABLE IF NOT EXISTS agentes (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, clave TEXT NOT NULL, nombre TEXT NOT NULL, creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(usuario_id,clave), FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE)');
    $columnas = $pdo->query('PRAGMA table_info(notificaciones)')->fetchAll();
    if (!in_array('agente_id', array_column($columnas,'name'), true)) {
        $pdo->exec('ALTER TABLE notificaciones ADD COLUMN agente_id INTEGER REFERENCES agentes(id)');
    }
    $pdo->exec('CREATE INDEX IF NOT EXISTS idx_notificaciones_agente ON notificaciones(usuario_id,agente_id,id)');
    $stmt = $pdo->prepare('SELECT id FROM usuarios WHERE usuario = ?');
    $stmt->execute(['jocarsa']);
    if (!$stmt->fetch()) {
        $stmt = $pdo->prepare('INSERT INTO usuarios(usuario,password_hash) VALUES(?,?)');
        $stmt->execute(['jocarsa', password_hash('jocarsa', PASSWORD_DEFAULT)]);
    }
    return $pdo;
}
function json_response(array $data, int $status = 200): never {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    header('X-Content-Type-Options: nosniff');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}
function input(): array {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw ?: '', true);
    return is_array($data) ? $data : $_POST;
}
function token_from_request(): string {
    return trim((string)($_SERVER['HTTP_X_SESSION_TOKEN'] ?? ''));
}
function require_user(PDO $db): array {
    $token = token_from_request();
    if (!preg_match('/^[a-f0-9]{64}$/', $token)) json_response(['ok'=>false,'error'=>'Sesión no válida'],401);
    $stmt = $db->prepare('SELECT u.id,u.usuario FROM sesiones s JOIN usuarios u ON u.id=s.usuario_id WHERE s.token_hash=? AND s.expira>? LIMIT 1');
    $stmt->execute([hash('sha256',$token), time()]);
    $user = $stmt->fetch();
    if (!$user) json_response(['ok'=>false,'error'=>'Sesión caducada o no válida'],401);
    return $user;
}
