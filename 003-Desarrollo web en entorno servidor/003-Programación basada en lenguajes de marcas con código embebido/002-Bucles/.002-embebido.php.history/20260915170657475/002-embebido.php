<!doctype html>
<html>
	<head>
  	<style>
    	main{display:grid;}
      .dia{border:1px solid grey;}
    </style>
  </head>
  <body>
  	<main>
      <?php
        for($dia = 1;$dia <= 31;$dia++){
          echo "<div class='dia'>".$dia."</div>";
        }
      ?>
    </main>
  </body>
</html>