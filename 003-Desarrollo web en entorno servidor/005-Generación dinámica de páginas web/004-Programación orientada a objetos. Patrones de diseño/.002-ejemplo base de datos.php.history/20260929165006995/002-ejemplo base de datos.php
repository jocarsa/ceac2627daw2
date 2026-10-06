<?php
  function dameDatos($tabla){
    $db = new PDO('sqlite:clientes.db');
    $info = $db->query("SELECT * FROM ".$tabla);
    return $info->fetchAll(PDO::FETCH_ASSOC);
  }

  function insertaDatos($tabla,$datos){
    $db = new PDO('sqlite:clientes.db');
    $info = $db->query("INSERT INTO ".$tabla." VALUES(".$datos.")");
    return 0;
  }
?>