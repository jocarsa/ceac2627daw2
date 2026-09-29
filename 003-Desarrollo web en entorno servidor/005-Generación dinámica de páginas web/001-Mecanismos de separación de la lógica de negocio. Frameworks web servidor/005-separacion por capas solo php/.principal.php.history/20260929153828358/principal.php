<?php
	include "controlador.php";
  include "vista.php";
  
  $datos = dameDatos("clientes");
  pintaTabla($datos);
?>