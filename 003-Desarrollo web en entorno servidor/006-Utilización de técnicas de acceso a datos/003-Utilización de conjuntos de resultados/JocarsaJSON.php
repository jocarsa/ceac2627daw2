<?php

class JocarsaJSON {

    public function guardarJSON($archivo, $datos) {
        $json = json_encode($datos, JSON_PRETTY_PRINT);
        file_put_contents($archivo, $json);
    }

    public function cargarJSON($archivo) {
        $json = file_get_contents($archivo);
        return json_decode($json, true);
    }

}
?>