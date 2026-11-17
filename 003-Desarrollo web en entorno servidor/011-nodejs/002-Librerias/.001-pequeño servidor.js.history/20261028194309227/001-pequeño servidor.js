// Cargo la librería de node http
const http = require('http');

// Creo un serrvidor, que espera una petición y una respuesta
http.createServer((peticion, respuesta) => {
  respuesta.write('Hola mundo desde node!');
  respuesta.end();
}).listen(3001); // Escucho en el puerto 3001

console.log('El servidor está corriendo en http://localhost:3001/');