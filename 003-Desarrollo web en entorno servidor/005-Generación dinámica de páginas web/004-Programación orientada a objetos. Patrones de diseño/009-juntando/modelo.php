<?php

class JocarsaModelo {

    private $bd;

    public function __construct($basededatos) {
        $this->bd = new PDO('sqlite:' . $basededatos);
        $this->bd->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }

    // Método normal
    public function dameDatos($tabla) {
        $info = $this->bd->query("SELECT * FROM " . $tabla);
        return $info->fetchAll(PDO::FETCH_ASSOC);
    }

    // Método estático
    public static function dameDatosEstatico($basededatos, $tabla) {
        $bd = new PDO('sqlite:' . $basededatos);
        $bd->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        $info = $bd->query("SELECT * FROM " . $tabla);

        return $info->fetchAll(PDO::FETCH_ASSOC);
    }

    public function insertaDatos($tabla, $datos) {
        $this->bd->query(
            "INSERT INTO " . $tabla . " VALUES(" . $datos . ")"
        );

        return 0;
    }

    public function eliminaDatos($tabla, $id) {
        $this->bd->query(
            "DELETE FROM " . $tabla . " WHERE id = " . $id
        );

        return 0;
    }
}

?>