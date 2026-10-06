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
  	<?php include "includes/login.php" ?>
  <?php
  }	
  ?>
<?php include "includes/final.php";?>