<?php

// Incluimos nuestro motor de base de datos CSV
require_once "JocarsaCSV.php";


// =============================================
// 1. CONECTAMOS CON EL MOTOR
// =============================================

$db = new JocarsaCSV("datos");


// =============================================
// 2. CREAR BASE DE DATOS
// =============================================

$db->crearBaseDatos("empresa");

echo "Base de datos creada<br>";


// =============================================
// 3. CREAR TABLA
// =============================================

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

echo "Tabla creada<br>";


// =============================================
// 4. INSERTAR REGISTROS
// =============================================

$db->insertar(
    "empresa",
    "clientes",
    [
        "id" => 1,
        "nombre" => "Ana",
        "apellidos" => "Garcia",
        "email" => "ana@correo.com",
        "telefono" => "600111111"
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
        "telefono" => "600222222"
    ]
);

$db->insertar(
    "empresa",
    "clientes",
    [
        "id" => 3,
        "nombre" => "Carlos",
        "apellidos" => "Lopez",
        "email" => "carlos@correo.com",
        "telefono" => "600333333"
    ]
);

echo "Registros insertados<br>";


// =============================================
// 5. LISTAR
// Equivalente a:
// SELECT * FROM clientes
// =============================================

echo "<h2>Todos los clientes</h2>";

echo "<pre>";

print_r(
    $db->listar("empresa", "clientes")
);

echo "</pre>";


// =============================================
// 6. BUSCAR
// Equivalente a:
// SELECT * FROM clientes
// WHERE nombre = 'Elena'
// =============================================

echo "<h2>Buscar Elena</h2>";

echo "<pre>";

print_r(
    $db->buscar(
        "empresa",
        "clientes",
        "nombre",
        "Elena"
    )
);

echo "</pre>";


// =============================================
// 7. ACTUALIZAR
// Equivalente a:
// UPDATE clientes
// SET telefono = '666666666'
// WHERE id = 2
// =============================================

$db->actualizar(
    "empresa",
    "clientes",
    "id",
    2,
    [
        "telefono" => "666666666",
        "email" => "elena.nueva@correo.com"
    ]
);

echo "<h2>Después del UPDATE</h2>";

echo "<pre>";

print_r(
    $db->listar("empresa", "clientes")
);

echo "</pre>";


// =============================================
// 8. ELIMINAR
// Equivalente a:
// DELETE FROM clientes
// WHERE id = 1
// =============================================

$db->eliminar(
    "empresa",
    "clientes",
    "id",
    1
);

echo "<h2>Después del DELETE</h2>";

echo "<pre>";

print_r(
    $db->listar("empresa", "clientes")
);

echo "</pre>";

?>