<?php

$json = file_get_contents("cv.json");
$cv = json_decode($json, true);

print_r($cv);

?>