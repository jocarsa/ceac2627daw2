<?php
	session_start();
  
  $db = new SQLite3('empresa.db');
  $result = $db->query("
  	SELECT * FROM usuarios 
    WHERE
    usuario = '".$_POST['usuario']."'
    AND
    contrasena = '".$_POST['contrasena']."';
    ");
    if ($fila = $result->fetchArray(SQLITE3_ASSOC)) {
    	 $_SESSION['llave'] = "jocarsa"; 						// En ese caso te doy la llave
      setcookie("llave", "jocarsa");
      header("Location:index.php"); 			// Vamos al escritorio
    }else{
    	header("Location:index.php");	// Volvemos al login
    }
    $db->close();
  
  
?>