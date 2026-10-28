const http = require('http');

let contador = 1;

http.createServer((peticion, respuesta) => {
  contador++;
  
  respuesta.write('<h1>Hola mundo desde node!<h1>');
  respuesta.end();
}).listen(3001);

console.log('El servidor está corriendo en http://localhost:3001/');