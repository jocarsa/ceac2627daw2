<?php

    $db=new SQLite3('clientes.db');
    $info = $db->query("SELECT * FROM clientes;"); 
    while($fila = $info->fetchArray(SQLITE3_ASSOC)){ 
      echo '<tr>
      	<td>'.$fila['nombre'].'</td>
        <td>'.$fila['apellidos'].'</td>
        <td>'.$fila['email'].'</td>
      </tr>'; 
    }

  ?>