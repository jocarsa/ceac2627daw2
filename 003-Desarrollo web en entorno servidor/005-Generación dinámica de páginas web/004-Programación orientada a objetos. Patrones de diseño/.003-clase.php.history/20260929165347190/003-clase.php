<?php
	class JocarsaModelo{
  	dameDatos($tabla){
    $db = new PDO('sqlite:clientes.db');
    $info = $db->query("SELECT * FROM ".$tabla);
    return $info->fetchAll(PDO::FETCH_ASSOC);
    }

    insertaDatos($tabla,$datos){
      $db = new PDO('sqlite:clientes.db');
      $info = $db->query("INSERT INTO ".$tabla." VALUES(".$datos.")");
      return 0;
    }

    eliminaDatos($tabla,$id){
      $db = new PDO('sqlite:clientes.db');
      $info = $db->query("DELETE FROM ".$tabla." WHERE id = ".$id."");
      return 0;
    }
  }
?>