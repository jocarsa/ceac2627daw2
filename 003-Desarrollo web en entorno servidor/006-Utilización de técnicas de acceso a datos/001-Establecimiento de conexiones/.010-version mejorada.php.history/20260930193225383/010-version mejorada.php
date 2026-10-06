<?php

$nombre = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";

// Cargar imagen PNG
$image = imagecreatefrompng("negra.png");

// Mantener el canal alfa
imagealphablending($image, false);
imagesavealpha($image, true);

$anchura = imagesx($image);
$altura  = imagesy($image);

$x = 0;
$y = 0;

// Procesamos 4 caracteres por píxel
for ($i = 0; $i < strlen($nombre); $i += 4) {

    // Comprobar que todavía queda espacio
    if ($y >= $altura) {
        die("No hay suficiente espacio en la imagen");
    }

    // R
    $r = isset($nombre[$i])
        ? ord($nombre[$i])
        : 0;

    // G
    $g = isset($nombre[$i + 1])
        ? ord($nombre[$i + 1])
        : 0;

    // B
    $b = isset($nombre[$i + 2])
        ? ord($nombre[$i + 2])
        : 0;

    // A
    // GD usa alfa 0-127
    $a = isset($nombre[$i + 3])
        ? ord($nombre[$i + 3]) % 128
        : 0;

    $color = imagecolorallocatealpha(
        $image,
        $r,
        $g,
        $b,
        $a
    );

    imagesetpixel(
        $image,
        $x,
        $y,
        $color
    );

    // Avanzamos horizontalmente
    $x++;

    // Si llegamos al final de la fila
    // saltamos a la siguiente
    if ($x >= $anchura) {
        $x = 0;
        $y++;
    }
}

// PNG sin compresión
imagepng(
    $image,
    "resultadoloco.png",
    0
);

imagedestroy($image);

echo "Texto escrito en la imagen";

?>