<?php
declare(strict_types=1);
require __DIR__ . '/config.php';
header('X-Content-Type-Options: nosniff');
$db = db();
$input = json_decode(file_get_contents('php://input'),true);
if (!is_array($input)) $input=[];
$action = $input['accion'] ?? $_GET['accion'] ?? '';
$method = $_SERVER['REQUEST_METHOD'];
if ($action === 'login' && $method === 'POST') {
    $stmt=$db->prepare('SELECT * FROM usuarios WHERE usuario=?');
    $stmt->execute([(string)($input['usuario'] ?? '')]);
    $u=$stmt->fetch();
    if (!$u || !password_verify((string)($input['password'] ?? ''),$u['password_hash'])) respond(['error'=>'Credenciales incorrectas'],401);
    $token=bin2hex(random_bytes(32));
    $db->prepare('INSERT INTO sesiones(token_hash,usuario_id,expira) VALUES(?,?,?)')->execute([hash('sha256',$token),$u['id'],time()+604800]);
    respond(['token'=>$token,'usuario'=>$u['usuario'],'expira_en'=>604800]);
}
$user=currentUser($db);
if ($action === 'listar' && $method === 'GET') {
    $stmt=$db->prepare('SELECT id,titulo,descripcion,icono,fecha,leida FROM notificaciones WHERE usuario_id=? ORDER BY id DESC LIMIT 200');
    $stmt->execute([$user['id']]);
    respond(['notificaciones'=>$stmt->fetchAll()]);
}
if ($action === 'enviar' && $method === 'POST') {
    $titulo=trim((string)($input['titulo'] ?? ''));
    $descripcion=trim((string)($input['descripcion'] ?? ''));
    $icono=trim((string)($input['icono'] ?? '🔔'));
    if ($titulo==='' || $descripcion==='' || mb_strlen($titulo)>150 || mb_strlen($descripcion)>5000 || mb_strlen($icono)>16) respond(['error'=>'Título o descripción inválidos'],422);
    $stmt=$db->prepare('INSERT INTO notificaciones(usuario_id,titulo,descripcion,icono) VALUES(?,?,?,?)');
    $stmt->execute([$user['id'],$titulo,$descripcion,$icono ?: '🔔']);
    respond(['ok'=>true,'id'=>(int)$db->lastInsertId()],201);
}
if ($action === 'leer' && $method === 'POST') {
    $id=filter_var($input['id'] ?? null,FILTER_VALIDATE_INT);
    if (!$id || $id<1) respond(['error'=>'ID inválido'],422);
    $stmt=$db->prepare('UPDATE notificaciones SET leida=1 WHERE id=? AND usuario_id=?');
    $stmt->execute([$id,$user['id']]);
    respond(['ok'=>true]);
}
if ($action === 'cambiar_password' && $method === 'POST') {
    $actual=(string)($input['actual'] ?? '');
    $nueva=(string)($input['nueva'] ?? '');
    $stmt=$db->prepare('SELECT password_hash FROM usuarios WHERE id=?');
    $stmt->execute([$user['id']]);
    if (!password_verify($actual,$stmt->fetchColumn())) respond(['error'=>'Contraseña actual incorrecta'],403);
    if (strlen($nueva)<12) respond(['error'=>'La contraseña nueva debe tener al menos 12 caracteres'],422);
    $db->prepare('UPDATE usuarios SET password_hash=? WHERE id=?')->execute([password_hash($nueva,PASSWORD_DEFAULT),$user['id']]);
    $db->prepare('DELETE FROM sesiones WHERE usuario_id=?')->execute([$user['id']]);
    respond(['ok'=>true]);
}
if ($action === 'logout' && $method === 'POST') {
    $header=$_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '';
    if (preg_match('/^Bearer ([a-f0-9]{64})$/i',$header,$m)) $db->prepare('DELETE FROM sesiones WHERE token_hash=?')->execute([hash('sha256',$m[1])]);
    respond(['ok'=>true]);
}
respond(['error'=>'Ruta o método no válido'],404);
