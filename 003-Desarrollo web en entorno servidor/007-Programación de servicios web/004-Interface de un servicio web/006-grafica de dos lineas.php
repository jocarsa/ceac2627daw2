<?php

$curl = curl_init("https://www.aemet.es/xml/municipios/localidad_46250.xml");
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$respuesta = curl_exec($curl);
curl_close($curl);

$xml = simplexml_load_string($respuesta);

// Arrays donde guardaremos los datos
$fechas = [];
$maximas = [];
$minimas = [];

// Extraemos temperaturas
foreach($xml->prediccion->dia as $dia){

    $fechas[] = (string)$dia["fecha"];
    $maximas[] = (int)$dia->temperatura->maxima;
    $minimas[] = (int)$dia->temperatura->minima;

}

?>

<!doctype html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Temperaturas AEMET</title>

<style>

body{
    font-family:Arial, sans-serif;
    background:#f5f5f5;
}

main{
    width:900px;
    margin:40px auto;
    background:white;
    padding:30px;
    border-radius:10px;
}

svg{
    width:100%;
    height:400px;
    border:1px solid #ddd;
}

.maxima{
    fill:none;
    stroke:red;
    stroke-width:3;
}

.minima{
    fill:none;
    stroke:blue;
    stroke-width:3;
}

text{
    font-size:12px;
    fill:#555;
}

</style>

</head>

<body>

<main>

<h1>Predicción de temperaturas</h1>

<svg viewBox="0 0 800 400">

<?php

$ancho = 800;
$alto = 400;

$margenIzquierdo = 50;
$margenSuperior = 30;
$margenInferior = 50;

$altoGrafica = $alto - $margenSuperior - $margenInferior;

$temperaturaMaxima = max($maximas) + 5;
$temperaturaMinima = min($minimas) - 5;

$rango = $temperaturaMaxima - $temperaturaMinima;

$numeroDias = count($fechas);

$separacionX = ($ancho - 100) / ($numeroDias - 1);


// -------------------------
// Líneas horizontales
// -------------------------

for($t = $temperaturaMinima; $t <= $temperaturaMaxima; $t += 5){

    $y = $margenSuperior +
         ($temperaturaMaxima - $t) / $rango * $altoGrafica;

    echo '
    <line
        x1="50"
        y1="'.$y.'"
        x2="750"
        y2="'.$y.'"
        stroke="#ddd"
    />

    <text
        x="10"
        y="'.($y+4).'"
    >
        '.$t.'º
    </text>
    ';
}


// -------------------------
// Línea temperaturas máximas
// -------------------------

$puntosMaximas = "";

for($i = 0; $i < $numeroDias; $i++){

    $x = $margenIzquierdo + $i * $separacionX;

    $y = $margenSuperior +
         ($temperaturaMaxima - $maximas[$i])
         / $rango
         * $altoGrafica;

    $puntosMaximas .= $x.",".$y." ";

}

echo '<polyline class="maxima" points="'.$puntosMaximas.'" />';


// -------------------------
// Línea temperaturas mínimas
// -------------------------

$puntosMinimas = "";

for($i = 0; $i < $numeroDias; $i++){

    $x = $margenIzquierdo + $i * $separacionX;

    $y = $margenSuperior +
         ($temperaturaMaxima - $minimas[$i])
         / $rango
         * $altoGrafica;

    $puntosMinimas .= $x.",".$y." ";

}

echo '<polyline class="minima" points="'.$puntosMinimas.'" />';


// -------------------------
// Puntos + fechas
// -------------------------

for($i = 0; $i < $numeroDias; $i++){

    $x = $margenIzquierdo + $i * $separacionX;

    $yMax = $margenSuperior +
            ($temperaturaMaxima - $maximas[$i])
            / $rango
            * $altoGrafica;

    $yMin = $margenSuperior +
            ($temperaturaMaxima - $minimas[$i])
            / $rango
            * $altoGrafica;

    // Punto máxima
    echo '
    <circle
        cx="'.$x.'"
        cy="'.$yMax.'"
        r="5"
        fill="red"
    />';

    // Valor máxima
    echo '
    <text
        x="'.$x.'"
        y="'.($yMax-10).'"
        text-anchor="middle"
        fill="red"
    >
        '.$maximas[$i].'º
    </text>';

    // Punto mínima
    echo '
    <circle
        cx="'.$x.'"
        cy="'.$yMin.'"
        r="5"
        fill="blue"
    />';

    // Valor mínima
    echo '
    <text
        x="'.$x.'"
        y="'.($yMin+20).'"
        text-anchor="middle"
        fill="blue"
    >
        '.$minimas[$i].'º
    </text>';

    // Fecha
    echo '
    <text
        x="'.$x.'"
        y="380"
        text-anchor="middle"
    >
        '.substr($fechas[$i],5).'
    </text>';

}

?>

</svg>

<p>
    🔴 Temperatura máxima
    &nbsp;&nbsp;&nbsp;
    🔵 Temperatura mínima
</p>

</main>

</body>
</html>