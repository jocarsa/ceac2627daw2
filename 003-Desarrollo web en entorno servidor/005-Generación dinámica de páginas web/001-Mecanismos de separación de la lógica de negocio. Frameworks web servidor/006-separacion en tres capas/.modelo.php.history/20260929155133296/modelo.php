<?php
function dameDatos($tabla){
    $db = new PDO('sqlite:clientes.db');

    $info = $db->query("SELECT * FROM ".$tabla);

    return $info->fetchAll(PDO::FETCH_ASSOC);
}

var_dump(dameDatos("clientes"));
?>