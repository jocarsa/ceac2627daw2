<?php

class JocarsaCSV {

    private $archivo;

    public function __construct($archivo) {
        $this->archivo = $archivo;
    }

    // Equivalente a SELECT * FROM tabla
    public function listar() {

        $archivo = fopen($this->archivo, "r");

        $cabeceras = fgetcsv($archivo);

        $conjunto = [];

        while (($fila = fgetcsv($archivo)) !== false) {
            $conjunto[] = array_combine($cabeceras, $fila);
        }

        fclose($archivo);

        return $conjunto;
    }

    // Equivalente a SELECT * FROM tabla WHERE columna = valor
    public function buscar($columna, $valor) {

        $datos = $this->listar();

        $resultados = [];

        foreach ($datos as $fila) {

            if (isset($fila[$columna]) && $fila[$columna] == $valor) {
                $resultados[] = $fila;
            }

        }

        return $resultados;
    }
}


// =============================
// EJEMPLO DE USO
// =============================

$clientes = new JocarsaCSV("datos.csv");


// SELECT *
//var_dump($clientes->listar());


// WHERE nombre = Jose Vicente
var_dump(
    $clientes->buscar("nombre", "Elena")
);

?>