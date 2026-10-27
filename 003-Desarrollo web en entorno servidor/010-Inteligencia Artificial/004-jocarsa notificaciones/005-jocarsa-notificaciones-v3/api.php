<?php
declare(strict_types=1);
require __DIR__ . '/config.php';
header('Referrer-Policy: same-origin');
try {
    $db = db();
    $data = input();
    $accion = (string)($_GET['accion'] ?? $data['accion'] ?? '');
    $method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
    if ($accion === 'login') {
        if ($method !== 'POST') json_response(['ok'=>false,'error'=>'Método no permitido'],405);
        $usuario = trim((string)($data['usuario'] ?? ''));
        $password = (string)($data['password'] ?? '');
        $stmt = $db->prepare('SELECT * FROM usuarios WHERE usuario=? LIMIT 1');
        $stmt->execute([$usuario]);
        $user = $stmt->fetch();
        if (!$user || !password_verify($password,$user['password_hash'])) json_response(['ok'=>false,'error'=>'Usuario o contraseña incorrectos'],401);
        $token = bin2hex(random_bytes(32));
        $db->prepare('DELETE FROM sesiones WHERE expira <= ?')->execute([time()]);
        $db->prepare('INSERT INTO sesiones(usuario_id,token_hash,expira) VALUES(?,?,?)')->execute([$user['id'],hash('sha256',$token),time()+86400*SESSION_DAYS]);
        json_response(['ok'=>true,'token'=>$token,'usuario'=>$user['usuario']]);
    }
    $user = require_user($db);
    if ($accion === 'listar') {
        if ($method !== 'GET') json_response(['ok'=>false,'error'=>'Método no permitido'],405);
        $stmt = $db->prepare('SELECT id,titulo,descripcion,icono,leida,creada FROM notificaciones WHERE usuario_id=? ORDER BY id DESC LIMIT 300');
        $stmt->execute([$user['id']]);
        json_response(['ok'=>true,'notificaciones'=>$stmt->fetchAll()]);
    }
    if ($accion === 'enviar') {
        if ($method !== 'POST') json_response(['ok'=>false,'error'=>'Método no permitido'],405);
        $titulo = trim((string)($data['titulo'] ?? ''));
        $descripcion = trim((string)($data['descripcion'] ?? ''));
        $icono = trim((string)($data['icono'] ?? '🔔')) ?: '🔔';
        if ($titulo === '' || $descripcion === '') json_response(['ok'=>false,'error'=>'Título y descripción son obligatorios'],422);
        if (mb_strlen($titulo)>160 || mb_strlen($descripcion)>4000 || mb_strlen($icono)>12) json_response(['ok'=>false,'error'=>'Contenido demasiado largo'],422);
        $stmt = $db->prepare('INSERT INTO notificaciones(usuario_id,titulo,descripcion,icono) VALUES(?,?,?,?)');
        $stmt->execute([$user['id'],$titulo,$descripcion,$icono]);
        json_response(['ok'=>true,'id'=>(int)$db->lastInsertId()],201);
    }
    if ($accion === 'leer') {
        if ($method !== 'POST') json_response(['ok'=>false,'error'=>'Método no permitido'],405);
        $id = filter_var($data['id'] ?? null,FILTER_VALIDATE_INT);
        if (!$id || $id < 1) json_response(['ok'=>false,'error'=>'ID inválido'],422);
        $stmt=$db->prepare('UPDATE notificaciones SET leida=1 WHERE id=? AND usuario_id=?');
        $stmt->execute([$id,$user['id']]);
        json_response(['ok'=>true]);
    }
    if ($accion === 'cambiar_password') {
        if ($method !== 'POST') json_response(['ok'=>false,'error'=>'Método no permitido'],405);
        $actual=(string)($data['actual'] ?? '');
        $nueva=(string)($data['nueva'] ?? '');
        $stmt=$db->prepare('SELECT password_hash FROM usuarios WHERE id=?');
        $stmt->execute([$user['id']]);
        if (!password_verify($actual,(string)$stmt->fetchColumn())) json_response(['ok'=>false,'error'=>'Contraseña actual incorrecta'],403);
        if (strlen($nueva)<12) json_response(['ok'=>false,'error'=>'La nueva contraseña debe tener al menos 12 caracteres'],422);
        $db->prepare('UPDATE usuarios SET password_hash=? WHERE id=?')->execute([password_hash($nueva,PASSWORD_DEFAULT),$user['id']]);
        $db->prepare('DELETE FROM sesiones WHERE usuario_id=?')->execute([$user['id']]);
        json_response(['ok'=>true,'mensaje'=>'Contraseña actualizada; vuelve a iniciar sesión']);
    }
    if ($accion === 'logout') {
        if ($method !== 'POST') json_response(['ok'=>false,'error'=>'Método no permitido'],405);
        $db->prepare('DELETE FROM sesiones WHERE token_hash=?')->execute([hash('sha256',token_from_request())]);
        json_response(['ok'=>true]);
    }
    json_response(['ok'=>false,'error'=>'Acción desconocida'],404);
} catch (Throwable $e) {
    error_log('Notificaciones: '.$e->getMessage());
    json_response(['ok'=>false,'error'=>'Error interno del servidor'],500);
}
