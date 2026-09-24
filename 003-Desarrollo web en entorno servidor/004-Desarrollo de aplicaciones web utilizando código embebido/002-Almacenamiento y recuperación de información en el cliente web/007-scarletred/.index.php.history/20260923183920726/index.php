<!doctype html>
<html>
	<head>
		<link rel="stylesheet" href="css/estilo.css">
	</head>
	<body>
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
				
				<h2><?php echo $tabla; ?></h2>
				
				<form action="?tabla=<?php echo $tabla; ?>" method="POST">
					<?php
						$db = new SQLite3('empresa.db');
						$result = $db->query("PRAGMA table_info(".$tabla.")");
						$campos = [];
						
						while ($column = $result->fetchArray(SQLITE3_ASSOC)) {
							$campos[] = $column['name'];
							echo "<input type='text' name='".$column['name']."' placeholder='".$column['name']."'><br>";
						}
						
						if(isset($_POST['insertar'])){
							$valores = [];
							
							foreach($campos as $campo){
								$valores[] = "'".$_POST[$campo]."'";
							}
							
							$sql = "INSERT INTO ".$tabla." VALUES(".implode(",", $valores).")";
							$db->exec($sql);
						}
						
						$db->close();
					?>
					
					<input type="submit" name="insertar">
				</form>
				
				<table border="1">
					<?php
						$db = new SQLite3('empresa.db');
						$result = $db->query("SELECT * FROM ".$tabla);
						
						while ($fila = $result->fetchArray(SQLITE3_ASSOC)) {
							echo "<tr>";
							
							foreach ($fila as $valor) {
								echo "<td>".$valor."</td>";
							}
							
							echo "</tr>";
						}
						
						$db->close();
					?>
				</table>
			</section>
		</main>
	</body>
</html>