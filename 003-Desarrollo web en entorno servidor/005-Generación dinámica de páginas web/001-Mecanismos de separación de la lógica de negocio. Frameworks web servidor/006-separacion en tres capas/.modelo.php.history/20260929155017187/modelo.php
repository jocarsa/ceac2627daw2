<?php
	function dameDatos($tabla){
    $db=new SQLite3('clientes.db');
    $info = $db->query("SELECT * FROM ".$tabla.";");
    var_dump($info);
  }
  
  dameDatos($tabla)
?>