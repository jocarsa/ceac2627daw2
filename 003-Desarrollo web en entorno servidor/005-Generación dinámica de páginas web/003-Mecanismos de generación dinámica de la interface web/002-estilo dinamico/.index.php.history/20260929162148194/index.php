<!doctype html>
<html>
	<head>
  	<style>
    	:root{
      	--colorcorporativo:red;
      }
    	html,body{padding:0px;margin:0px;width:100%;height:100%;}
      body{display:flex;flex-direction:column;}
      header{background:var(--colorcorporativo);padding:10px;}
      main{display:flex;height:100%;}
      nav{background:var(--colorcorporativo);flex:1;padding:10px;}
      section{flex:9;}
    </style>
  </head>
  <body>
  	<header>
    	jocarsa | software
    </header>
    <main>
    	<nav>	
      Hola
      </nav>
      <section>
      </section>
    </main>
    <script>
    	fetch("leeconfiguracion.php")
      .then(function(resultado){return resultado.json()})
      .then(function(datos){
      	console.log(datos)
      })
    </script>
  </body>
</html>