const http = require('http');

http.createServer((peticion, respuesta) => {
  respuesta.write('<h1>Hola mundo desde node!<h1>');
  respuesta.end();
}).listen(3001);

console.log('El servidor está corriendo en http://localhost:3001/');