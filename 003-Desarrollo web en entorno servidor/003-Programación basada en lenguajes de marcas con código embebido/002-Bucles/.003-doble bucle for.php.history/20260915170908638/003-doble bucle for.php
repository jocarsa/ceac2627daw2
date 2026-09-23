<!doctype html>
<html>
	<head>
  	<style>
    	main{display:grid; grid-template-columns: repeat(7, 1fr);
      font-family:sans-serif;}
      .dia{border:1px solid grey;height:40px;padding:5px;}
    </style>
  </head>
  <body>
  	<main>
      <?php
      	for($mes = 1;$mes <= 12;$mes++){
          for($dia = 1;$dia <= 31;$dia++){
            echo "<div class='dia'>".$dia."</div>";
          }
        }
      ?>
    </main>
  </body>
</html>