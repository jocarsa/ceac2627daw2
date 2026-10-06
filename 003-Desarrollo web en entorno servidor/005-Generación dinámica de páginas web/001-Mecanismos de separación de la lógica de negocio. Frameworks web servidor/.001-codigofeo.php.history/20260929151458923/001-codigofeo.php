<?php

	$db=new SQLite3('clientes.db');
  $info = $db->query("SELECT * FROM clientes;); 
  while($info->fetchArray(SQLITE3_ASSOC)){ $campos[]=$c['name']; if($c['pk']==1)$pk=$c['name']; }
  if(isset($_GET['eliminar']) && $pk){
      $st=$db->prepare("DELETE FROM ".$tabla." WHERE ".$pk."=:id");
      $st->bindValue(':id',$_GET['eliminar']); $st->execute();
      header("Location:?tabla=".urlencode($tabla)); exit();
  }
	
?>