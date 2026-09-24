<?php
	session_start();
	if(
    $_POST['usuario'] == "jocarsa" 								// Si el usuario es jocarsa
    && 
    $_POST['contrasena'] == "jocarsa"							// Y la contraseña es jocarsa
    ){
      $_SESSION['llave'] == "jocarsa"; 						// En ese caso te doy la llave
      header("Location:007-escritorio.php"); 			// Vamos al escritorio
    }else{
    	header("Location:005-inicio de sesion.php");	// Volvemos al login
    }
?>