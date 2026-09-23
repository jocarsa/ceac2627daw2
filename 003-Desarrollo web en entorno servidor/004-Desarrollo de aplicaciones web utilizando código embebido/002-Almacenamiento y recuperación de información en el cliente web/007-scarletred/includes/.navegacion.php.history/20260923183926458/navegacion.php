<?php
  $db = new SQLite3('../empresa.db');
  $result = $db->query("SELECT name FROM sqlite_master WHERE type='table'");
  while ($fila = $result->fetchArray(SQLITE3_ASSOC)) {
  echo "<a href='?tabla=".$fila['name']."'><button>".$fila['name']."</button></a>";
  }
  $db->close();
?>