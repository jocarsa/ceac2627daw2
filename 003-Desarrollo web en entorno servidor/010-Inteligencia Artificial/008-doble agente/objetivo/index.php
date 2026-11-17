<?php
session_start();
require 'config.php';
require 'functions.php';

$action = isset($_GET['action']) ? $_GET['action'] : 'list';

switch ($action) {
    case 'list':
        $clients = getAllClients();
        break;
    case 'add':
        if ($_SERVER['REQUEST_METHOD'] == 'POST') {
            addClient($_POST['name'], $_POST['email']);
            header('Location: index.php?action=list');
            exit();
        }
        break;
    case 'edit':
        $id = $_GET['id'];
        $client = getClientById($id);
        if ($_SERVER['REQUEST_METHOD'] == 'POST') {
            updateClient($id, $_POST['name'], $_POST['email']);
            header('Location: index.php?action=list');
            exit();
        }
        break;
    case 'delete':
        $id = $_GET['id'];
        deleteClient($id);
        header('Location: index.php?action=list');
        exit();
}

?><!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aplicación CRUD</title>
    <link rel="stylesheet" href="estilo.css">
</head>
<body>
    <h1>Aplicación CRUD</h1>
    <nav>
        <a href="index.php?action=list">Listar Clientes</a>
        <a href="index.php?action=add">Añadir Cliente</a>
    </nav>
    <main>
        <?php if ($action == 'list'): ?>
            <h2>Listado de Clientes</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($clients as $client): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($client['id']); ?></td>
                            <td><?php echo htmlspecialchars($client['name']); ?></td>
                            <td><?php echo htmlspecialchars($client['email']); ?></td>
                            <td>
                                <a href="index.php?action=edit&id=<?php echo htmlspecialchars($client['id']); ?>" class="btn-edit">Editar</a>
                                <a href="index.php?action=delete&id=<?php echo htmlspecialchars($client['id']); ?>" class="btn-delete">Eliminar</a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php elseif ($action == 'add'): ?>
            <h2>Añadir Cliente</h2>
            <form action="index.php?action=add" method="post">
                <label for="name">Nombre:</label>
                <input type="text" id="name" name="name" required>
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
                <button type="submit" class="btn-submit">Añadir</button>
            </form>
        <?php elseif ($action == 'edit'): ?>
            <h2>Editar Cliente</h2>
            <form action="index.php?action=edit&id=<?php echo htmlspecialchars($id); ?>