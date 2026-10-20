PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS comentarios (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 id_post INTEGER NOT NULL REFERENCES publicaciones(id) ON DELETE CASCADE,
 id_persona INTEGER NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
 fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 contenido TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_comentarios_post ON comentarios(id_post,fecha,id);
CREATE INDEX IF NOT EXISTS idx_conexiones_destino ON conexiones(id_persona_destino);
CREATE INDEX IF NOT EXISTS idx_publicaciones_fecha ON publicaciones(fecha DESC,id DESC);