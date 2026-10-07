<?php

$db = new PDO("sqlite:municipios.db");

$resultado = $db->query("
	SELECT * FROM diccionario26
  WHERE NOMBRE LIKE '%".$_GET['clave']."%'
  ;
  ");

while ($fila = $resultado->fetch(PDO::FETCH_ASSOC)) {
    echo $fila["NOMBRE"] . ",";
}

?>