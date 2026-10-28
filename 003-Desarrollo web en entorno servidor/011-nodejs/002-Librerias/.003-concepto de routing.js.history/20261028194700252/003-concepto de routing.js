const http = require('http');

const server = http.createServer((peticion, respuesta) => {
  if (peticion.url === '/') {
    respuesta.write('Bienvenidos a mi web');
  } else if (peticion.url === '/sobremi') {
    respuesta.write('Bienvenidos a sobre mi');
  } else {
    respuesta.statusCode = 404;
    respuesta.write('404 Not Found');
  }
  respuesta.end();
});

server.listen(3001, () => {
  console.log('Servidor corriendo en: http://localhost:3000/');
});