<?php
  $db = new SQLite3('empresa.db');
  $result = $db->query("SELECT * FROM roles WHERE rol='".$_SESSION['rol']."'");
  while ($fila = $result->fetchArray(SQLITE3_ASSOC)) {
 
  echo "<a href='?tabla=".$fila['name']."'><button>".$fila['name']."</button></a>";
  }
  $db->close();
?>