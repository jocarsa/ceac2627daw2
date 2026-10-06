<?php

class JocarsaModelo {

    private $bd;

    public function __construct($basededatos) {
        $this->bd = new PDO('sqlite:' . $basededatos);
        $this->bd->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }

    public function dameDatos($tabla) {
        $info = $this->bd->query("SELECT * FROM " . $tabla);
        return $info->fetchAll(PDO::FETCH_ASSOC);
    }

    public function insertaDatos($tabla, $datos) {
        $info = $this->bd->query(
            "INSERT INTO " . $tabla . " VALUES(" . $datos . ")"
        );
        return 0;
    }

    public function eliminaDatos($tabla, $id) {
        $info = $this->bd->query(
            "DELETE FROM " . $tabla . " WHERE id = " . $id
        );
        return 0;
    }
}

?>