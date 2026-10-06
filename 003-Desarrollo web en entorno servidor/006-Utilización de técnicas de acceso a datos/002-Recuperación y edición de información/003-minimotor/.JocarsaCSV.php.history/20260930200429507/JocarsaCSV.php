<?php

class JocarsaCSV {

    private $rutaBase;

    public function __construct($rutaBase = "datos") {
        $this->rutaBase = rtrim($rutaBase, "/");
    }


    // =====================================================
    // BASES DE DATOS
    // Una base de datos es una carpeta
    // =====================================================

    public function crearBaseDatos($nombre) {

        $ruta = $this->rutaBase . "/" . $nombre;

        if (!is_dir($ruta)) {
            mkdir($ruta, 0777, true);
        }

        return true;
    }


    // =====================================================
    // TABLAS
    // Una tabla es un archivo CSV
    // =====================================================

    public function crearTabla($basedatos, $tabla, $columnas) {

        $carpeta = $this->rutaBase . "/" . $basedatos;

        // Si no existe la BD, la creamos
        if (!is_dir($carpeta)) {
            $this->crearBaseDatos($basedatos);
        }

        $ruta = $carpeta . "/" . $tabla . ".csv";

        $archivo = fopen($ruta, "w");

        // Primera fila = nombres de columnas
        fputcsv($archivo, $columnas);

        fclose($archivo);

        return true;
    }


    // =====================================================
    // RUTA DE UNA TABLA
    // =====================================================

    private function rutaTabla($basedatos, $tabla) {

        return $this->rutaBase
            . "/"
            . $basedatos
            . "/"
            . $tabla
            . ".csv";
    }


    // =====================================================
    // READ
    // SELECT * FROM tabla
    // =====================================================

    public function listar($basedatos, $tabla) {

        $ruta = $this->rutaTabla($basedatos, $tabla);

        if (!file_exists($ruta)) {
            return [];
        }

        $archivo = fopen($ruta, "r");

        $cabeceras = fgetcsv($archivo);

        $conjunto = [];

        while (($fila = fgetcsv($archivo)) !== false) {

            $conjunto[] = array_combine(
                $cabeceras,
                $fila
            );
        }

        fclose($archivo);

        return $conjunto;
    }


    // =====================================================
    // READ
    // SELECT * FROM tabla WHERE columna = valor
    // =====================================================

    public function buscar($basedatos, $tabla, $columna, $valor) {

        $datos = $this->listar($basedatos, $tabla);

        $resultados = [];

        foreach ($datos as $fila) {

            if (
                isset($fila[$columna])
                &&
                $fila[$columna] == $valor
            ) {

                $resultados[] = $fila;
            }
        }

        return $resultados;
    }


    // =====================================================
    // CREATE
    // INSERT INTO tabla
    // =====================================================

    public function insertar($basedatos, $tabla, $datos) {

        $ruta = $this->rutaTabla($basedatos, $tabla);

        if (!file_exists($ruta)) {
            return false;
        }

        // Leer las columnas
        $archivo = fopen($ruta, "r");
        $cabeceras = fgetcsv($archivo);
        fclose($archivo);


        // Ordenar los datos según las columnas
        $fila = [];

        foreach ($cabeceras as $columna) {

            $fila[] = $datos[$columna] ?? "";
        }


        // Añadir al CSV
        $archivo = fopen($ruta, "a");

        fputcsv($archivo, $fila);

        fclose($archivo);

        return true;
    }


    // =====================================================
    // UPDATE
    // UPDATE tabla SET ... WHERE columna = valor
    // =====================================================

    public function actualizar(
        $basedatos,
        $tabla,
        $columna,
        $valor,
        $nuevosDatos
    ) {

        $ruta = $this->rutaTabla($basedatos, $tabla);

        // Cargamos TODA la tabla en memoria
        $datos = $this->listar($basedatos, $tabla);

        if (!file_exists($ruta)) {
            return false;
        }


        // Modificamos los registros en memoria
        foreach ($datos as &$fila) {

            if (
                isset($fila[$columna])
                &&
                $fila[$columna] == $valor
            ) {

                foreach ($nuevosDatos as $campo => $nuevoValor) {

                    if (array_key_exists($campo, $fila)) {
                        $fila[$campo] = $nuevoValor;
                    }
                }
            }
        }

        unset($fila);


        // Recuperamos cabeceras
        $archivo = fopen($ruta, "r");

        $cabeceras = fgetcsv($archivo);

        fclose($archivo);


        // Reescribimos TODO el CSV
        $archivo = fopen($ruta, "w");

        fputcsv($archivo, $cabeceras);

        foreach ($datos as $fila) {

            $filaOrdenada = [];

            foreach ($cabeceras as $columnaCSV) {
                $filaOrdenada[] = $fila[$columnaCSV];
            }

            fputcsv($archivo, $filaOrdenada);
        }

        fclose($archivo);

        return true;
    }


    // =====================================================
    // DELETE
    // DELETE FROM tabla WHERE columna = valor
    // =====================================================

    public function eliminar(
        $basedatos,
        $tabla,
        $columna,
        $valor
    ) {

        $ruta = $this->rutaTabla($basedatos, $tabla);

        if (!file_exists($ruta)) {
            return false;
        }


        // Cargamos toda la tabla
        $datos = $this->listar($basedatos, $tabla);


        // Filtramos
        $nuevosDatos = [];

        foreach ($datos as $fila) {

            if (
                !isset($fila[$columna])
                ||
                $fila[$columna] != $valor
            ) {

                $nuevosDatos[] = $fila;
            }
        }


        // Cabeceras
        $archivo = fopen($ruta, "r");

        $cabeceras = fgetcsv($archivo);

        fclose($archivo);


        // Reescribir archivo
        $archivo = fopen($ruta, "w");

        fputcsv($archivo, $cabeceras);

        foreach ($nuevosDatos as $fila) {

            $filaOrdenada = [];

            foreach ($cabeceras as $columnaCSV) {
                $filaOrdenada[] = $fila[$columnaCSV];
            }

            fputcsv($archivo, $filaOrdenada);
        }

        fclose($archivo);

        return true;
    }
}



// =========================================================
// EJEMPLO DE USO
// =========================================================

$db = new JocarsaCSV("datos");


// ---------------------------------------------------------
// CREATE DATABASE empresa
// ---------------------------------------------------------

$db->crearBaseDatos("empresa");


// ---------------------------------------------------------
// CREATE TABLE clientes
// ---------------------------------------------------------

$db->crearTabla(
    "empresa",
    "clientes",
    [
        "id",
        "nombre",
        "apellidos",
        "email",
        "telefono"
    ]
);


// ---------------------------------------------------------
// INSERT
// ---------------------------------------------------------

$db->insertar(
    "empresa",
    "clientes",
    [
        "id" => 1,
        "nombre" => "Jose Vicente",
        "apellidos" => "Carratala",
        "email" => "info@jocarsa.com",
        "telefono" => "600000001"
    ]
);


$db->insertar(
    "empresa",
    "clientes",
    [
        "id" => 2,
        "nombre" => "Elena",
        "apellidos" => "Martinez",
        "email" => "elena@correo.com",
        "telefono" => "600000002"
    ]
);


// ---------------------------------------------------------
// SELECT *
// ---------------------------------------------------------

echo "<pre>";

print_r(
    $db->listar("empresa", "clientes")
);


// ---------------------------------------------------------
// SELECT WHERE
// ---------------------------------------------------------

print_r(
    $db->buscar(
        "empresa",
        "clientes",
        "nombre",
        "Elena"
    )
);


// ---------------------------------------------------------
// UPDATE
// ---------------------------------------------------------

$db->actualizar(
    "empresa",
    "clientes",
    "id",
    2,
    [
        "email" => "nuevo@correo.com",
        "telefono" => "666666666"
    ]
);


// ---------------------------------------------------------
// DELETE
// ---------------------------------------------------------

$db->eliminar(
    "empresa",
    "clientes",
    "id",
    1
);


echo "</pre>";

?>