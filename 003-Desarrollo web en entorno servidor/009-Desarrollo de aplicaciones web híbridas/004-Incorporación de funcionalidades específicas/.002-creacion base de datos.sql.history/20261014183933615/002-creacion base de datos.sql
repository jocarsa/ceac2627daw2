
PRAGMA foreign_keys = ON;

CREATE TABLE personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    usuario TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL
);

CREATE TABLE publicaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona INTEGER NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    contenidos TEXT NOT NULL,
    FOREIGN KEY (id_persona)
        REFERENCES personas(id)
);

CREATE TABLE reacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_post INTEGER NOT NULL,
    id_persona INTEGER NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT NOT NULL,
    FOREIGN KEY (id_post)
        REFERENCES publicaciones(id),
    FOREIGN KEY (id_persona)
        REFERENCES personas(id)
);

CREATE TABLE conexiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona_origen INTEGER NOT NULL,
    id_persona_destino INTEGER NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_persona_origen)
        REFERENCES personas(id),
    FOREIGN KEY (id_persona_destino)
        REFERENCES personas(id),
    UNIQUE (id_persona_origen, id_persona_destino),
    CHECK (id_persona_origen != id_persona_destino)
);
