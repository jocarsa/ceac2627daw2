<?php
$config = [
    'nombre' => 'ScarletRed',
    'logo' => 'S',
    'subtitulo' => 'Panel de administración CSV',
    'color' => '#b32d2e',
    'ruta_datos' => __DIR__ . '/datos',
    'basededatos' => 'empresa',
    // En CSV no hay metadatos de PK: declaramos la clave por tabla.
    'claves_primarias' => [
        'usuarios'=>'Identificador','roles'=>'Identificador','clientes'=>'Identificador',
        'empleados'=>'Identificador','categorias'=>'id','proveedores'=>'id','productos'=>'id',
        'almacenes'=>'id','inventario'=>'id','pedidos'=>'id','lineas_pedido'=>'id',
        'facturas'=>'id','pagos'=>'id'
    ]
];
