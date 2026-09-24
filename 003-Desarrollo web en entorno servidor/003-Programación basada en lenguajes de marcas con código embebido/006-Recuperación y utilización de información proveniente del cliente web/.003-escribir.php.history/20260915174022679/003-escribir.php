<?php
	$archivo = fopen("prueba.txt",'w');
  fwrite($archivo,"esto es una prueba");
  fclose($archivo);
?>	