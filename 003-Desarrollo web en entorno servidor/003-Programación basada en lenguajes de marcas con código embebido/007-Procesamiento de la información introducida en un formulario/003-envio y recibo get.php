<?php
	echo "Yo soy GET y te digo:";
  echo $_GET['nombre'];
?>
<form action="?" method="GET">
  <input type="text" name="nombre">
  <input type="submit">
</form>