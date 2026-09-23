<?php
$db = new SQLite3('empresa.db');
$stmt = $db->prepare("SELECT * FROM roles WHERE idrol=:rol");
$stmt->bindValue(':rol', $_SESSION['rol'] ?? '', SQLITE3_TEXT);
$result = $stmt->execute();
while($fila = $result->fetchArray(SQLITE3_ASSOC)){
    $t = $fila['tabla'];
    echo "<a class='nav-link' href='?tabla=".urlencode($t)."'>".htmlspecialchars(ucfirst($t))."</a>";
}
$db->close();
?>
