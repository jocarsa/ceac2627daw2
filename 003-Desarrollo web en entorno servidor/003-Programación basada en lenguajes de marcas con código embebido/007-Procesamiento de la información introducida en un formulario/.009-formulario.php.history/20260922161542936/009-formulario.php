<?php

$db = new SQLite3('empresa.db');
$result = $db->query("PRAGMA table_info(clientes)");
while ($column = $result->fetchArray(SQLITE3_ASSOC)) {
    echo $column['name'] . "<br>";
}
$db->close();

?>