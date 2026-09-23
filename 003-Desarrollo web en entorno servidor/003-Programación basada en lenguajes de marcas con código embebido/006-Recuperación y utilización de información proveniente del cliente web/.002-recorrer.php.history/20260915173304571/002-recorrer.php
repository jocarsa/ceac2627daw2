<?php
$servidor = $_SERVER;

foreach ($servidor as $clave => $valor) {
    echo $clave . ": " . $valor;
    echo "<br>";
}
?>