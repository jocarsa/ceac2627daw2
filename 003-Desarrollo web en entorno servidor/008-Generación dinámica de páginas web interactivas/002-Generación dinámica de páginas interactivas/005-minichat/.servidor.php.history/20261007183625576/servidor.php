<?php
	$accion = $_GET['accion'];
  $db = new PDO("sqlite:chat.db");

  switch($accion){
  	case "get":
    	// Dame  todos los mensajes
      $resultado = $db->query("SELECT * FROM mensajes");
      $mensajes = [];
      while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
          $mensajes[] = $fila;
      }
      echo json_encode($mensajes;)
      break;
    case "post":
    	// Te envío un mensaje
      break;
  }
?>