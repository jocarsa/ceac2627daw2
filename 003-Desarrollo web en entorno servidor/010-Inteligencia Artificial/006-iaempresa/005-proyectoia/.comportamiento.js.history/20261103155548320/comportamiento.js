let entrada = document.querySelector("input")
let mensajes = document.querySelector("main section")
entrada.onkeyup = function(e){
  if(e.key == "Enter"){
    // Atrapo el valor del input
    let valor = this.value
    // Lo pongo en los mensajes
    mensajes.innerHTML += `
          	<article class="usuario">
            `+valor+`
            </article>
          `
    // Vacío el input
    this.value = ""
    // Lo envío al servidor
    fetch("servidor.php?mensaje="+encodeURI(valor))
      .then(function(retorno){return retorno.text()})
      .then(function(datos){
      console.log(datos)
      mensajes.innerHTML += `
              <article class="ia">
              `+datos+`
              </article>
            `
    })
  }
}