-Personas
	-id
	-nombre
  -apellidos
  -email
  
-Publicaciones
	-id
  -id_persona
  -fecha
  -contenidos

-Reacciones
	-id
  -id_post
  -id_persona
  -fecha
  -tipo
  
-Conexiones
	-id
  -id_persona_origen
  -id_persona_destino
  -fecha