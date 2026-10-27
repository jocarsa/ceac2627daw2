let plantilla = document.querySelector("#publicacion")
let contenedor = document.querySelector("#publicaciones")

for(let i = 0;i<50;i++){
	let instancia = plantilla.content.cloneNode(true)
  contenedor.appendChild(instancia)
}