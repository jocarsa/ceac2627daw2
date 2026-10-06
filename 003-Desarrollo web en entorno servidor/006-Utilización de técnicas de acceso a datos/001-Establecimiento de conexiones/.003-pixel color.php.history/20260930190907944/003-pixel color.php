<?php

// Load the image
$image = imagecreatefromjpeg("josevicente.jpeg");

// Get the color of the pixel at the specified position
$color = imagecolorat($image, $x, $y);

// Free the image resource
imagedestroy($image);

// Return the color as a hexadecimal string
return '#' . dechex($color);
}

// Example usage
$imagePath = 'path/to/your/image.jpg';
$x = 100;
$y = 50;
$pixelColor = getPixelColor($imagePath, $x, $y);
echo "The color of the pixel at ($x, $y) is: " . $pixelColor;
?>