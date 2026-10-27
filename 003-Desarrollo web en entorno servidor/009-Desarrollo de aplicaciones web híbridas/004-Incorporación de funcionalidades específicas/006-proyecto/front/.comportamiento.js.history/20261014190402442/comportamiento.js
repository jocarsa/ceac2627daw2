let plantilla = document.querySelector("#publicacion")
let contenedor = document.querySelector("#publicaciones")

fetch("api.php")
.then(function(resultado){return resultado.json()})
	let instancia = plantilla.content.cloneNode(true)
  contenedor.appendChild(instancia)
}