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