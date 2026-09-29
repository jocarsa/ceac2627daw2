<?php
    $db=new SQLite3('clientes.db');
    $info = $db->query("SELECT * FROM clientes;"); 
    $json = [];
    while($fila = $info->fetchArray(SQLITE3_ASSOC)){ 
       $json[] = $fila;
    }
		echo json_encode($json);
?>