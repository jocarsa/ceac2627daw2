<?php

$nombre = "Jose Vicente";

$image = imagecreatefrompng("negra.png");

$anchura = imagesx($image);
$altura  = imagesy($image);

$x = 0;
$y = 0;

// Recorremos de 3 en 3: R, G, B
for($i = 0; $i < strlen($nombre); $i += 3){

    // ROJO
    $r = isset($nombre[$i])
        ? ord($nombre[$i])
        : 0;

    // VERDE
    $g = isset($nombre[$i + 1])
        ? ord($nombre[$i + 1])
        : 0;

    // AZUL
    $b = isset($nombre[$i + 2])
        ? ord($nombre[$i + 2])
        : 0;

    // Alfa = 0 en GD significa 100% opaco
    $a = 0;

    $color = imagecolorallocatealpha(
        $image,
        $r,
        $g,
        $b,
        $a
    );

    imagesetpixel($image, $x, $y, $color);

    // Siguiente píxel
    $x++;

    // Si llegamos al final, siguiente línea
    if($x >= $anchura){
        $x = 0;
        $y++;
    }

    // Si llenamos toda la imagen
    if($y >= $altura){
        break;
    }
}

// PNG sin compresión
imagepng($image, "resultadoloco.png", 0);

imagedestroy($image);

echo "Texto escrito";

?>