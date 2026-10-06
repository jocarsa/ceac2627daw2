<?php
session_start();
require_once 'modelo.php';
require_once 'controlador.php';
$modelo = new JocarsaModelo(__DIR__.'/empresa.db');
$controlador = new JocarsaControlador($modelo);
$controlador->logout();
header('Location:index.php');
exit();
