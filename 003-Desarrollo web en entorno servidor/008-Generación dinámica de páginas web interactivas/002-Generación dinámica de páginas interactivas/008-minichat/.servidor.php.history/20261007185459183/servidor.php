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
      echo json_encode($mensajes);
      break;
    case "post":
    	// Te envío un mensaje
      $fecha = date('Y')."-".date('m')."-".date('d')." ".date('H').":".date('i').":".date('s');
      $resultado = $db->query("
      	INSERT INTO mensajes
        VALUES(
        	NULL,
          '".$_GET['usuario']."',
          '".$fecha."',
          '".$_GET['mensaje']."'
        );
      ");
      break;
  }
?>