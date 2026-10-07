<?php

$accion = $_GET['accion'] ?? '';

try {

    $db = new PDO("sqlite:chat.db");

    // Hacer que PDO muestre los errores de SQLite
    $db->setAttribute(
        PDO::ATTR_ERRMODE,
        PDO::ERRMODE_EXCEPTION
    );

    switch($accion){

        case "get":

            $resultado = $db->query("
                SELECT * 
                FROM mensajes
                ORDER BY id ASC
            ");

            $mensajes = [];

            while(
                $fila = $resultado->fetch(PDO::FETCH_ASSOC)
            ){
                $mensajes[] = $fila;
            }

            header("Content-Type: application/json");

            echo json_encode($mensajes);

            break;


        case "post":

            $usuario = $_GET['usuario'] ?? '';
            $mensaje = $_GET['mensaje'] ?? '';

            $fecha = date("Y-m-d H:i:s");

            $sql = "
                INSERT INTO mensajes
                (usuario, fecha, mensaje)
                VALUES
                (:usuario, :fecha, :mensaje)
            ";

            $consulta = $db->prepare($sql);

            $consulta->execute([
                ":usuario" => $usuario,
                ":fecha"   => $fecha,
                ":mensaje" => $mensaje
            ]);

            header("Content-Type: application/json");

            echo json_encode([
                "ok" => true,
                "id" => $db->lastInsertId(),
                "usuario" => $usuario,
                "fecha" => $fecha,
                "mensaje" => $mensaje
            ]);

            break;


        default:

            http_response_code(400);

            echo json_encode([
                "ok" => false,
                "error" => "Acción no válida"
            ]);

    }

}
catch(PDOException $e){

    http_response_code(500);

    header("Content-Type: application/json");

    echo json_encode([
        "ok" => false,
        "error" => $e->getMessage()
    ]);

}
?>