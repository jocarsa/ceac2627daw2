<?php
	function dameDatos($tabla){
    $db=new SQLite3('clientes.db');
    $info = $db->query("SELECT * FROM ".$tabla.";"); 
    $json = [];
    while($fila = $info->fetchArray(SQLITE3_ASSOC)){ 
       $json[] = $fila;
    }
		return json_encode($json);
  }
?>