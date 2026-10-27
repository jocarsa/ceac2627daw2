-- Ejecutar una sola vez sobre red.db, tras realizar copia de seguridad.
ALTER TABLE personas ADD COLUMN perfil_publico INTEGER NOT NULL DEFAULT 0 CHECK(perfil_publico IN (0,1));
CREATE INDEX IF NOT EXISTS idx_personas_perfil_publico ON personas(perfil_publico);
