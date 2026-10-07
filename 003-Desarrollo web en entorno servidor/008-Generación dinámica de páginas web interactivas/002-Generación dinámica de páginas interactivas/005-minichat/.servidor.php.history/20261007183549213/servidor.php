<?php
	$accion = $_GET['accion'];
  $db = new PDO("sqlite:chat.db");

  

  while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
      echo $fila["NOMBRE"] . "<br>";
  }
  switch($accion){
  	case "get":
    	// Dame  todos los mensajes
      $resultado = $db->query("SELECT * FROM mensajes");
      break;
    case "post":
    	// Te envío un mensaje
      break;
  }
?>