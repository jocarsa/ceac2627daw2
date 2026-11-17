<?php
session_start();
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/Clases/modelo.php';
require_once __DIR__ . '/Clases/controlador.php';
require_once __DIR__ . '/Clases/vista.php';

$modelo = new JocarsaModelo($config['basededatos']);
$controlador = new JocarsaControlador($modelo);
$vista = new JocarsaVista($config);
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
