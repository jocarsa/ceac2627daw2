-Empresa

  -Usuarios (la empresa tiene usuarios)

    -Conversaciones (el usuario tiene conversaciones)

      -Mensajes (las conversaciones tienen mensajes)
      
CREATE TABLE "empresa" (
	"id"	INTEGER,
	"nombre"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)

CREATE TABLE "usuarios" (
	"id"	INTEGER,
	"usuario"	TEXT,
	"contrasena"	TEXT,
	"nombre"	TEXT,
	"apellidos"	TEXT,
	"email"	TEXT,
	"id_empresa"	INTEGER,
	FOREIGN KEY("id_empresa") REFERENCES "empresa"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)

CREATE TABLE "conversaciones" (
	"id"	INTEGER,
	"titulo"	TEXT,
	"fecha"	TEXT,
	"id_usuario"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("id_usuario") REFERENCES "usuarios"("id")
)

CREATE TABLE "mensajes" (
	"id"	INTEGER,
	"mensaje"	TEXT,
	"emisor"	TEXT,
	"fecha"	TEXT,
	"id_conversacion"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("id_conversacion") REFERENCES "conversaciones"("id")
)