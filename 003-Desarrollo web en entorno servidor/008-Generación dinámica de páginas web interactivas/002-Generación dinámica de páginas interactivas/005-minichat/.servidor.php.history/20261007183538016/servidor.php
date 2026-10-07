<?php
	$accion = $_GET['accion'];
  $db = new PDO("sqlite:chat.db");

  $resultado = $db->query("SELECT * FROM diccionario26");

  while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
      echo $fila["NOMBRE"] . "<br>";
  }
  switch($accion){
  	case "get":
    	// Dame  todos los mensajes
      
      break;
    case "post":
    	// Te envío un mensaje
      break;
  }
?>