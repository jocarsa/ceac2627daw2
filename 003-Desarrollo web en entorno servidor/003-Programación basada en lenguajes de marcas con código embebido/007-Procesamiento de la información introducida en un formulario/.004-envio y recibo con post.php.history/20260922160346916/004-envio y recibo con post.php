<?php
	echo "Yo soy GET y te digo:";
  echo $_POST['nombre'];
?>
<form action="?" method="POST">
  <input type="text" name="nombre">
  <input type="submit">
</form>