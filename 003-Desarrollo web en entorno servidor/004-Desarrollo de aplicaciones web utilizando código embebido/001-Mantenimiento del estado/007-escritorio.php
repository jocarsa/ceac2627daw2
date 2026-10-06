<?php
	session_start();
  if(!isset($_SESSION['llave'])){ // Si no existe la variable llave
  	die("No tienes permiso");			// Mata el proceso
  }else{
  	echo "Has entrado legalmente";
  }
?>