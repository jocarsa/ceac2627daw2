<?php
declare(strict_types=1);
ini_set('display_errors','0');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
ini_set('session.use_strict_mode','1');
ini_set('session.cookie_httponly','1');
ini_set('session.cookie_samesite','Lax');
if (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ini_set('session.cookie_secure','1');
session_start();
function respond($data, int $status=200): never { http_response_code($status); echo json_encode($data,JSON_UNESCAPED_UNICODE|JSON_INVALID_UTF8_SUBSTITUTE); exit; }
function fail(string $message,int $status=400): never {respond(['error'=>$message],$status);}
try {
 $db=new PDO('sqlite:'.__DIR__.'/ialocal.db',null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC,PDO::ATTR_TIMEOUT=>5]);
 $db->exec('PRAGMA foreign_keys=ON');
 $db->exec('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT, contrasena TEXT, nombre TEXT, apellidos TEXT, email TEXT, id_empresa INTEGER)');
 $db->exec('CREATE TABLE IF NOT EXISTS conversaciones (id INTEGER PRIMARY KEY, titulo TEXT, fecha TEXT, id_usuario INTEGER)');
 $db->exec('CREATE TABLE IF NOT EXISTS mensajes (id INTEGER PRIMARY KEY, mensaje TEXT, emisor TEXT, fecha TEXT, id_conversacion INTEGER)');
 $db->exec('CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_usuario ON usuarios(usuario)');
 $db->exec('CREATE INDEX IF NOT EXISTS idx_conv_usuario ON conversaciones(id_usuario)');
 $db->exec('CREATE INDEX IF NOT EXISTS idx_msg_conv ON mensajes(id_conversacion,id)');
 $action=$_GET['accion']??$_POST['accion']??'';
 if ($_SERVER['REQUEST_METHOD']!=='POST' && $action!=='sesion') fail('Método no permitido',405);
 $body=json_decode(file_get_contents('php://input'),true); if(!is_array($body))$body=$_POST;
 if($action==='sesion') {respond(['usuario'=>isset($_SESSION['uid'])?['id'=>$_SESSION['uid'],'nombre'=>$_SESSION['nombre']]:null,'csrf'=>$_SESSION['csrf']??null]);}
 if($action==='registro') {
  $usuario=trim((string)($body['usuario']??'')); $nombre=trim((string)($body['nombre']??'')); $email=trim((string)($body['email']??'')); $pass=(string)($body['contrasena']??'');
  if(!preg_match('/^[a-zA-Z0-9_.-]{3,40}$/',$usuario))fail('Usuario: entre 3 y 40 caracteres (letras, números, _, . o -)');
  if(mb_strlen($nombre)>100 || !$nombre)fail('Indica un nombre válido');
  if(!filter_var($email,FILTER_VALIDATE_EMAIL)||strlen($email)>254)fail('Correo no válido');
  if(strlen($pass)<10||strlen($pass)>256)fail('La contraseña debe tener entre 10 y 256 caracteres');
  $q=$db->prepare('INSERT INTO usuarios(usuario,contrasena,nombre,email) VALUES(?,?,?,?)');
  try{$q->execute([$usuario,password_hash($pass,PASSWORD_DEFAULT),$nombre,$email]);}catch(PDOException $e){if($e->getCode()==='23000')fail('El nombre de usuario ya existe',409);throw $e;}
  session_regenerate_id(true); $_SESSION=['uid'=>(int)$db->lastInsertId(),'nombre'=>$nombre,'csrf'=>bin2hex(random_bytes(24))]; respond(['usuario'=>['id'=>$_SESSION['uid'],'nombre'=>$nombre],'csrf'=>$_SESSION['csrf']]);
 }
 if($action==='login') {
  $q=$db->prepare('SELECT * FROM usuarios WHERE usuario=?');$q->execute([trim((string)($body['usuario']??''))]);$u=$q->fetch();
  if(!$u || !password_verify((string)($body['contrasena']??''),(string)$u['contrasena']))fail('Credenciales incorrectas',401);
  session_regenerate_id(true);$_SESSION=['uid'=>(int)$u['id'],'nombre'=>$u['nombre']?:$u['usuario'],'csrf'=>bin2hex(random_bytes(24))];respond(['usuario'=>['id'=>$_SESSION['uid'],'nombre'=>$_SESSION['nombre']],'csrf'=>$_SESSION['csrf']]);
 }
 if(!isset($_SESSION['uid']))fail('Debes iniciar sesión',401);
 if(!hash_equals($_SESSION['csrf']??'',(string)($_SERVER['HTTP_X_CSRF_TOKEN']??'')))fail('Token de sesión incorrecto',403);
 $uid=(int)$_SESSION['uid'];
 if($action==='logout'){$_SESSION=[];session_destroy();respond(['ok'=>true]);}
 if($action==='listar'){
  $q=$db->prepare('SELECT c.id,c.titulo,c.fecha,(SELECT MAX(m.id) FROM mensajes m WHERE m.id_conversacion=c.id) AS ultimo FROM conversaciones c WHERE c.id_usuario=? ORDER BY COALESCE(ultimo,0) DESC,c.id DESC');$q->execute([$uid]);respond(['conversaciones'=>$q->fetchAll()]);
 }
 if($action==='crear'){$q=$db->prepare('INSERT INTO conversaciones(titulo,fecha,id_usuario) VALUES(?,?,?)');$q->execute(['Nueva conversación',date('c'),$uid]);respond(['id'=>(int)$db->lastInsertId()]);}
 $id=filter_var($body['id']??null,FILTER_VALIDATE_INT,['options'=>['min_range'=>1]]);if(!$id)fail('Conversación no válida');
 $q=$db->prepare('SELECT id,titulo FROM conversaciones WHERE id=? AND id_usuario=?');$q->execute([$id,$uid]);$conv=$q->fetch();if(!$conv)fail('Conversación no encontrada',404);
 if($action==='mensajes'){$q=$db->prepare('SELECT id,mensaje,emisor,fecha FROM mensajes WHERE id_conversacion=? ORDER BY id');$q->execute([$id]);respond(['mensajes'=>$q->fetchAll(),'titulo'=>$conv['titulo']]);}
 if($action==='renombrar'){$titulo=trim((string)($body['titulo']??''));if(!$titulo||mb_strlen($titulo)>100)fail('Título no válido');$db->prepare('UPDATE conversaciones SET titulo=? WHERE id=?')->execute([$titulo,$id]);respond(['ok'=>true]);}
 if($action==='eliminar'){$db->beginTransaction();$db->prepare('DELETE FROM mensajes WHERE id_conversacion=?')->execute([$id]);$db->prepare('DELETE FROM conversaciones WHERE id=? AND id_usuario=?')->execute([$id,$uid]);$db->commit();respond(['ok'=>true]);}
 if($action==='enviar'){
  $mensaje=trim((string)($body['mensaje']??''));if(!$mensaje||mb_strlen($mensaje)>12000)fail('Mensaje vacío o demasiado largo');
  $db->prepare('INSERT INTO mensajes(mensaje,emisor,fecha,id_conversacion) VALUES(?,?,?,?)')->execute([$mensaje,'usuario',date('U'),$id]);
  $q=$db->prepare('SELECT mensaje,emisor FROM mensajes WHERE id_conversacion=? ORDER BY id DESC LIMIT 12');$q->execute([$id]);$hist=array_reverse($q->fetchAll());
  $contexto='';foreach($hist as $m)$contexto.=($m['emisor']==='usuario'?'Usuario':'Asistente').': '.$m['mensaje']."\n";$contexto.='Asistente: ';
  $payload=['model'=>'granite4.1:8b','system'=>"Responde en el idioma del usuario, con claridad y concisión.",'prompt'=>$contexto,'stream'=>false];
  $ch=curl_init('http://127.0.0.1:11434/api/generate');curl_setopt_array($ch,[CURLOPT_POST=>true,CURLOPT_POSTFIELDS=>json_encode($payload),CURLOPT_RETURNTRANSFER=>true,CURLOPT_HTTPHEADER=>['Content-Type: application/json'],CURLOPT_CONNECTTIMEOUT=>5,CURLOPT_TIMEOUT=>180]);$raw=curl_exec($ch);$err=curl_error($ch);$status=curl_getinfo($ch,CURLINFO_HTTP_CODE);curl_close($ch);
  $result=json_decode((string)$raw,true);if($raw===false||$status!==200||!isset($result['response']))fail('No se pudo obtener respuesta de Ollama. '.$err,502);
  $respuesta=(string)$result['response'];$db->prepare('INSERT INTO mensajes(mensaje,emisor,fecha,id_conversacion) VALUES(?,?,?,?)')->execute([$respuesta,'ia',date('U'),$id]);
  if($conv['titulo']==='Nueva conversación'){$titulo=mb_substr(preg_replace('/\s+/u',' ',$mensaje),0,65);$db->prepare('UPDATE conversaciones SET titulo=? WHERE id=?')->execute([$titulo,$id]);}
  respond(['respuesta'=>$respuesta]);
 }
 fail('Acción desconocida',404);
}catch(Throwable $e){error_log('proyectoia: '.$e->getMessage());fail('Error interno del servidor',500);}
