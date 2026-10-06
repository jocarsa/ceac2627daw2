<?php
	include "vista.php";
  include "modelo.php";
  include "controlador.php";
  
  $basededatos = new JocarsaModelo("clientes.db");
  $clientes = $basededatos->dameDatos("clientes");
  $json = coseJSON($clientes);

?>