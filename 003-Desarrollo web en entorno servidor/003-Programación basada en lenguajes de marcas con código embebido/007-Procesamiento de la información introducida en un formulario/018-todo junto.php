<!doctype html>
<html>
	<head>
		<style>
			*{
				box-sizing:border-box;
			}
			
			body{
				margin:0;
				font-family:Arial, sans-serif;
				background:#f0f0f1;
				color:#1d2327;
			}
			
			header{
				height:50px;
				background:#1d2327;
			}
			
			main{
				display:flex;
				min-height:calc(100vh - 50px);
			}
			
			nav{
				width:200px;
				background:#2c3338;
				padding:10px;
			}
			
			nav a{
				display:block;
				margin-bottom:5px;
			}
			
			nav button{
				width:100%;
				padding:10px;
				text-align:left;
				background:#2c3338;
				color:white;
				border:0;
				cursor:pointer;
			}
			
			nav button:hover{
				background:#2271b1;
			}
			
			section{
				flex:1;
				margin:20px;
				padding:20px;
				background:white;
				border:1px solid #c3c4c7;
				box-shadow:0 1px 1px rgba(0,0,0,0.04);
			}
			
			input{
				padding:8px;
				margin-bottom:5px;
			}
			
			table{
				margin-top:20px;
				border-collapse:collapse;
				width:100%;
			}
			
			td{
				padding:8px;
			}
		</style>
	</head>
	<body>
		<header>
		</header>
		<main>
			<nav>
				<?php
					$db = new SQLite3('empresa.db');
					$result = $db->query("SELECT name FROM sqlite_master WHERE type='table'");
					while ($fila = $result->fetchArray(SQLITE3_ASSOC)) {
						echo "<a href='?tabla=".$fila['name']."'><button>".$fila['name']."</button></a>";
					}
					$db->close();
				?>
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