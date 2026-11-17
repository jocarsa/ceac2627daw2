const http = require('http');

let cabecera = `
	<!doctype html>
  <html>
  	<head>
    </head>
    <body>
    	<header>
      	<h1>La web de Jose Vicente</h1>
        <nav>
        	<a href="/">Inicio</a>
          <a href="/sobremi">Sobre mi</a>
        </nav>
      </header>
      <main>
`

let piedepagina = `
			</main>
      <footer>
      </footer>
    <body>
  </html>
`

const server = http.createServer((peticion, respuesta) => {
  if (peticion.url === '/') {
    respuesta.write(cabecera+"Pagina de inicio"+piedepagina);
  } else if (peticion.url === '/sobremi') {
    respuesta.write(cabecera+"Sobre mi"+piedepagina);
  } else {
    respuesta.write(cabecera+"No encontrado"+piedepagina);
  }
  respuesta.end();
});

server.listen(3000, () => {
  console.log('Servidor corriendo en: http://localhost:3000/');
});