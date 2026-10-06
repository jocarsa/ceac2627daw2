<?php

$image = imagecreatefromjpeg("josevicente.jpeg");

$color = imagecolorat($image, 0, 0);

// Extraer RGB
$r = ($color >> 16) & 0xFF;
$g = ($color >> 8)  & 0xFF;
$b = $color & 0xFF;

imagedestroy($image);

echo "RGB: $r, $g, $b";

?>