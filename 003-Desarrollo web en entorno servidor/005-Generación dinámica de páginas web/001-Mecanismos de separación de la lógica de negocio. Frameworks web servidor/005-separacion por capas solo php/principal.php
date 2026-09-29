<?php
	include "controlador.php";
  include "vista.php";
  
  $datos = dameDatos("clientes");
  pintaTabla($datos);
  
  $datos = dameDatos("productos");
  pintaTabla($datos);
?>