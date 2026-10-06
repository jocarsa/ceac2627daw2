<?php
	session_start();
  if(!isset($_SESSION['llave'])){
  	die("No tienes permiso");
  }
?>