<form action="?" method="POST">
  <?php

  $db = new SQLite3('empresa.db');

  if(isset($_POST['insertar'])){
    $db->exec("
      INSERT INTO clientes VALUES(
        '".$_POST['nombre']."',
        '".$_POST['apellidos']."',
        '".$_POST['telefono']."',
        '".$_POST['email']."',
        NULL
      )
    ");
  }

  $result = $db->query("PRAGMA table_info(clientes)");
  while ($column = $result->fetchArray(SQLITE3_ASSOC)) {
      echo "<input type='text' name='".$column['name']."' placeholder='".$column['name']."'><br>";
  }

  $db->close();

  ?>
  <input type="submit" name="insertar">
</form>