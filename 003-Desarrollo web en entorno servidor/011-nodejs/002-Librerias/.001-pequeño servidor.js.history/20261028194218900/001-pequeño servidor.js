const http = require('http');

http.createServer((peticion, respuesta) => {
  respuesta.write('Hola mundo desde node!');
  respuesta.end();
}).listen(3000);

console.log('El servidor está corriendo en http://localhost:3000/');