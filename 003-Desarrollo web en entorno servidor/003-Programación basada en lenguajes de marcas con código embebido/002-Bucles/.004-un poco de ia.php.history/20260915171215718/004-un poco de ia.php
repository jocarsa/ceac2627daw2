<!doctype html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Calendario 2026</title>

    <style>
        *{
            box-sizing:border-box;
        }

        body{
            margin:0;
            padding:30px;
            background:#f4f4f4;
            font-family:Arial, sans-serif;
            color:#333;
        }

        h1{
            text-align:center;
            margin-bottom:40px;
        }

        .calendario{
            display:grid;
            grid-template-columns:repeat(3, 1fr);
            gap:25px;
            max-width:1200px;
            margin:auto;
        }

        .mes{
            background:white;
            border-radius:10px;
            padding:15px;
            box-shadow:0 3px 10px rgba(0,0,0,0.1);
        }

        .mes h2{
            text-align:center;
            margin:0 0 15px 0;
            text-transform:capitalize;
        }

        .dias-semana,
        .dias{
            display:grid;
            grid-template-columns:repeat(7, 1fr);
        }

        .nombre-dia{
            text-align:center;
            font-size:12px;
            font-weight:bold;
            padding:8px 2px;
            color:#777;
        }

        .dia{
            min-height:45px;
            border:1px solid #eee;
            padding:5px;
            text-align:center;
            display:flex;
            align-items:center;
            justify-content:center;
            transition:0.2s;
        }

        .dia:hover{
            background:#eee;
        }

        .vacio{
            min-height:45px;
        }

        .fin-semana{
            background:#fafafa;
        }

        @media(max-width:900px){
            .calendario{
                grid-template-columns:repeat(2, 1fr);
            }
        }

        @media(max-width:600px){
            .calendario{
                grid-template-columns:1fr;
            }
        }
    </style>
</head>

<body>

<h1>Calendario 2026</h1>

<div class="calendario">

<?php

$anyo = 2026;

$nombresMeses = [
    1 => "Enero",
    2 => "Febrero",
    3 => "Marzo",
    4 => "Abril",
    5 => "Mayo",
    6 => "Junio",
    7 => "Julio",
    8 => "Agosto",
    9 => "Septiembre",
    10 => "Octubre",
    11 => "Noviembre",
    12 => "Diciembre"
];

for($mes = 1; $mes <= 12; $mes++){

    // Número correcto de días del mes
    $diasMes = date("t", mktime(0, 0, 0, $mes, 1, $anyo));

    // Día de la semana del día 1
    // 1 = lunes ... 7 = domingo
    $primerDia = date("N", mktime(0, 0, 0, $mes, 1, $anyo));

    echo "<section class='mes'>";

    echo "<h2>".$nombresMeses[$mes]."</h2>";

    echo "
        <div class='dias-semana'>
            <div class='nombre-dia'>L</div>
            <div class='nombre-dia'>M</div>
            <div class='nombre-dia'>X</div>
            <div class='nombre-dia'>J</div>
            <div class='nombre-dia'>V</div>
            <div class='nombre-dia'>S</div>
            <div class='nombre-dia'>D</div>
        </div>
    ";

    echo "<div class='dias'>";

    // Celdas vacías antes del día 1
    for($i = 1; $i < $primerDia; $i++){
        echo "<div class='vacio'></div>";
    }

    // Días reales del mes
    for($dia = 1; $dia <= $diasMes; $dia++){

        $diaSemana = date(
            "N",
            mktime(0, 0, 0, $mes, $dia, $anyo)
        );

        $clase = "dia";

        if($diaSemana >= 6){
            $clase .= " fin-semana";
        }

        echo "<div class='$clase'>$dia</div>";
    }

    echo "</div>";
    echo "</section>";
}

?>

</div>

</body>
</html>