<?php
	$nombre = "Jose Vicente";
  $image = imagecreatefrompng("negra.png");
  
  for($i = 0;$i<strlen($nombre);$i++){
    $r = ord($nombre[$i]);
    $g = 0;
    $b = 0;

    $color = imagecolorallocate($image, $r, $g, $b);

    imagesetpixel($image, $i, 0, $color);
  }
  imagepng($image, "resultadoloco.png", 0);

	imagedestroy($image);
?>