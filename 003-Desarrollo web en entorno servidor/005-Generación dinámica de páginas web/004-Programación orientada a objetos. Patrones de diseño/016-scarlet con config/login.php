<?php
session_start();
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/Clases/modelo.php';
require_once __DIR__ . '/Clases/controlador.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location:index.php'); exit(); }
$modelo = new JocarsaModelo($config['basededatos']);
$controlador = new JocarsaControlador($modelo);
if ($controlador->login($_POST['usuario'] ?? '', $_POST['contrasena'] ?? '')) header('Location:index.php');
else header('Location:index.php?error=1');
exit();
