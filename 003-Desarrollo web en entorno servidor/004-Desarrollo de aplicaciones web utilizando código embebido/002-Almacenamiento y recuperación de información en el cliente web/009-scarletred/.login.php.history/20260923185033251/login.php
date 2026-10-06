<?php
	session_start();
	if(
    $_POST['usuario'] == "jocarsa" 								// Si el usuario es jocarsa
    && 
    $_POST['contrasena'] == "jocarsa"							// Y la contraseña es jocarsa
    ){
      $_SESSION['llave'] = "jocarsa"; 						// En ese caso te doy la llave
      setcookie("llave", "jocarsa");
      header("Location:index.php"); 			// Vamos al escritorio
    }else{
    	header("Location:ningunaparte.html");	// Volvemos al login
    }
?>