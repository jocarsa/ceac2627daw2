<?php session_start();?>
<?php include "includes/principio.php";?>
	<?php if(isset($_SESSION['llave'])){ ?>
		<header>
		</header>
		<main>
			<nav>
				<?php include "includes/navegacion.php" ?>
			</nav>
			<section>
				<?php
					$tabla = isset($_GET['tabla']) ? $_GET['tabla'] : "clientes";
				?>
				<?php include "includes/formulario.php"?>
				<?php include "includes/tabla.php"?>
			</section>
		</main>
  <?php }else{?>
  <!doctype html>
<html>
  <head>
    <style>
      body{
        font-family:Arial;
        background:#f0f0f1;
      }
      form{
        width:300px;
        margin:100px auto;
        padding:20px;
        background:white;
      }
      input{
        width:100%;
        padding:10px;
        margin:5px 0;
        box-sizing:border-box;
      }
    </style>
  </head>
  <body>
    <form method="POST" action="006-login.php">
      <input type="text" name="usuario" placeholder="Usuario">
      <input type="password" name="contrasena" placeholder="Contraseña">
      <input type="submit" value="Entrar">
    </form>
  </body>
</html>
  <?php
  }	
  ?>
<?php include "includes/final.php";?>