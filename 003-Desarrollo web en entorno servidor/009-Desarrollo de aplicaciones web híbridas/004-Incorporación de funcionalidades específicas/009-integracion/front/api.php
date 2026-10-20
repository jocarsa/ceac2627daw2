<?php
session_start();
header('Content-Type: application/json; charset=utf-8');
function responder($datos, $codigo=200){http_response_code($codigo);echo json_encode($datos,JSON_UNESCAPED_UNICODE|JSON_INVALID_UTF8_SUBSTITUTE);exit;}
try {
$db=new PDO('sqlite:'.__DIR__.'/../red.db');$db->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);$db->exec('PRAGMA foreign_keys=ON');
$accion=$_GET['accion']??'publicaciones';$id=(int)($_SESSION['usuario_id']??0);
$entrada=json_decode(file_get_contents('php://input'),true)??[];
if($accion==='login'){
 $s=$db->prepare('SELECT id,contrasena FROM personas WHERE usuario=:u');$s->execute([':u'=>trim($entrada['usuario']??'')]);$p=$s->fetch(PDO::FETCH_ASSOC);
 $clave=(string)($entrada['contrasena']??'');
 if(!$p || !(password_verify($clave,$p['contrasena']) || (hash_equals($p['contrasena'],$clave) && !password_get_info($p['contrasena'])['algo']))) responder(['error'=>'Credenciales incorrectas'],401);
 session_regenerate_id(true);$_SESSION['usuario_id']=(int)$p['id'];responder(['ok'=>true]);
}
if($accion==='logout'){$_SESSION=[];session_destroy();responder(['ok'=>true]);}
if(!$id)responder(['error'=>'No autenticado'],401);
if($accion==='perfil'){$s=$db->prepare('SELECT id,nombre,apellidos,email,usuario FROM personas WHERE id=?');$s->execute([$id]);responder($s->fetch(PDO::FETCH_ASSOC));}
if($accion==='usuarios'){
 $q=trim($_GET['q']??'');$s=$db->prepare('SELECT p.id,p.nombre,p.apellidos,p.usuario, EXISTS(SELECT 1 FROM conexiones c WHERE (c.id_persona_origen=:id AND c.id_persona_destino=p.id) OR (c.id_persona_destino=:id AND c.id_persona_origen=p.id)) AS conectado FROM personas p WHERE p.id<>:id AND (p.nombre LIKE :q OR p.apellidos LIKE :q OR p.usuario LIKE :q) ORDER BY conectado DESC,p.nombre,p.apellidos LIMIT 100');$s->execute([':id'=>$id,':q'=>'%'.$q.'%']);responder($s->fetchAll(PDO::FETCH_ASSOC));
}
if($accion==='conectar'){
 $otro=(int)($entrada['id']??0);if(!$otro||$otro===$id)responder(['error'=>'Usuario inválido'],400);
 $s=$db->prepare('SELECT 1 FROM personas WHERE id=?');$s->execute([$otro]);if(!$s->fetchColumn())responder(['error'=>'Usuario inexistente'],404);
 $s=$db->prepare('INSERT OR IGNORE INTO conexiones(id_persona_origen,id_persona_destino) VALUES(?,?)');$s->execute([$id,$otro]);responder(['ok'=>true]);
}
if($accion==='publicaciones'){
 $offset=max(0,(int)($_GET['offset']??0));$limite=min(50,max(1,(int)($_GET['limite']??10)));
 $s=$db->prepare('SELECT p.id,p.id_persona,p.fecha,p.contenidos,u.nombre,u.apellidos,(SELECT COUNT(*) FROM comentarios c WHERE c.id_post=p.id) AS num_comentarios FROM publicaciones p JOIN personas u ON u.id=p.id_persona WHERE p.id_persona=:id OR EXISTS(SELECT 1 FROM conexiones c WHERE (c.id_persona_origen=:id AND c.id_persona_destino=p.id_persona) OR (c.id_persona_destino=:id AND c.id_persona_origen=p.id_persona)) ORDER BY p.fecha DESC,p.id DESC LIMIT :limite OFFSET :offset');
 $s->bindValue(':id',$id,PDO::PARAM_INT);$s->bindValue(':limite',$limite,PDO::PARAM_INT);$s->bindValue(':offset',$offset,PDO::PARAM_INT);$s->execute();responder($s->fetchAll(PDO::FETCH_ASSOC));
}
if($accion==='comentarios'){
 $post=(int)($_GET['post']??0);$s=$db->prepare('SELECT c.id,c.contenido,c.fecha,u.nombre,u.apellidos FROM comentarios c JOIN personas u ON u.id=c.id_persona WHERE c.id_post=? AND EXISTS(SELECT 1 FROM publicaciones p WHERE p.id=c.id_post AND (p.id_persona=? OR EXISTS(SELECT 1 FROM conexiones x WHERE (x.id_persona_origen=? AND x.id_persona_destino=p.id_persona) OR (x.id_persona_destino=? AND x.id_persona_origen=p.id_persona)))) ORDER BY c.fecha,c.id');$s->execute([$post,$id,$id,$id]);responder($s->fetchAll(PDO::FETCH_ASSOC));
}
if($accion==='comentar'){
 $post=(int)($entrada['post']??0);$contenido=trim((string)($entrada['contenido']??''));if(!$contenido||mb_strlen($contenido)>3000)responder(['error'=>'Comentario vacío o demasiado largo'],400);
 $s=$db->prepare('SELECT 1 FROM publicaciones p WHERE p.id=? AND (p.id_persona=? OR EXISTS(SELECT 1 FROM conexiones c WHERE (c.id_persona_origen=? AND c.id_persona_destino=p.id_persona) OR (c.id_persona_destino=? AND c.id_persona_origen=p.id_persona)))');$s->execute([$post,$id,$id,$id]);if(!$s->fetchColumn())responder(['error'=>'Publicación no disponible'],403);
 $s=$db->prepare('INSERT INTO comentarios(id_post,id_persona,contenido) VALUES(?,?,?)');$s->execute([$post,$id,$contenido]);responder(['ok'=>true]);
}
responder(['error'=>'Acción desconocida'],404);
}catch(Throwable $e){error_log($e);responder(['error'=>'Error del servidor. Comprueba la base de datos y la migración.'],500);}