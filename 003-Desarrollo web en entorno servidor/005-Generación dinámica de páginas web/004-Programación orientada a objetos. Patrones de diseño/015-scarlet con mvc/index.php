<?php
session_start();
require_once 'modelo.php';
require_once 'controlador.php';
require_once 'vista.php';

$modelo = new JocarsaModelo(__DIR__.'/empresa.db');
$controlador = new JocarsaControlador($modelo);
$vista = new JocarsaVista();
$vista->principio();

if (!isset($_SESSION['llave'])) {
    $vista->login(isset($_GET['error']));
} else {
    $tablas = $controlador->tablasPermitidas();
    $tabla = $controlador->tablaSolicitada();
    $estado = $controlador->procesaCrud($tabla);
    $vista->abrePanel($_SESSION['nombre'] ?? 'Usuario', $tablas, $tabla, $estado['accion']);
    if ($estado['accion'] === 'nuevo' || $estado['accion'] === 'editar') {
        $vista->pintaFormulario($estado['campos'], $estado['registro'], $estado['pk'], $estado['accion']);
    } else {
        $vista->pintaTabla($estado['datos'], $estado['campos'], $estado['pk'], $tabla);
    }
    $vista->cierraPanel();
}
$vista->final();
