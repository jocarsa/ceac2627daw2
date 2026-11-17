<?php
if (PHP_SAPI !== 'cli') exit("Solo terminal\n");
if ($argc !== 3) exit("Uso: php crear_admin.php usuario contraseña\n");
$ruta=__DIR__.'/data/ialocal.db';
if (!is_file($ruta)) exit("Falta la base original data/ialocal.db\n");
$db=new PDO('sqlite:'.$ruta,null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
$cols=$db->query('PRAGMA table_info(usuarios)')->fetchAll(PDO::FETCH_ASSOC);
if (!$cols) exit("La tabla usuarios no existe en la base de IA\n");
if (!in_array('rol',array_column($cols,'name'),true)) $db->exec("ALTER TABLE usuarios ADD COLUMN rol TEXT DEFAULT 'usuario'");
$st=$db->prepare('SELECT id FROM usuarios WHERE usuario=?');$st->execute([$argv[1]]);$id=$st->fetchColumn();
$hash=password_hash($argv[2],PASSWORD_DEFAULT);
if ($id) {$st=$db->prepare("UPDATE usuarios SET contrasena=?,rol='admin' WHERE id=?");$st->execute([$hash,$id]);}
else {$st=$db->prepare("INSERT INTO usuarios(usuario,contrasena,nombre,rol) VALUES(?,?,'Administrador','admin')");$st->execute([$argv[1],$hash]);}
echo "Administrador preparado. Elimina crear_admin.php después de usarlo.\n";
