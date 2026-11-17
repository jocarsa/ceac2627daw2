<?php
if (PHP_SAPI!=='cli') {http_response_code(403);exit('Solo CLI');}
require __DIR__.'/data/inicializar.php';
if ($argc!==3) {fwrite(STDERR,"Uso: php crear_admin.php USUARIO CONTRASENA\n");exit(1);}
[$script,$usuario,$pass]=$argv;
if (!preg_match('/^[a-zA-Z0-9_.-]{3,40}$/',$usuario) || strlen($pass)<10) {fwrite(STDERR,"Usuario inválido o contraseña menor de 10 caracteres\n");exit(1);}
$db=jocarsa_db();
$q=$db->prepare('SELECT id FROM usuarios WHERE usuario=?');$q->execute([$usuario]);
if ($q->fetch()) {fwrite(STDERR,"El usuario ya existe; no se modifica automáticamente\n");exit(1);}
$q=$db->prepare("INSERT INTO usuarios(usuario,contrasena,nombre,rol) VALUES(?,?,?,'admin')");
$q->execute([$usuario,password_hash($pass,PASSWORD_DEFAULT),$usuario]);
echo "Administrador creado. Elimina crear_admin.php después de usarlo.\n";
