<?php
class JocarsaModelo {
    private PDO $bd;

    public function __construct(string $basededatos) {
        $this->bd = new PDO('sqlite:' . $basededatos);
        $this->bd->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $this->bd->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    }

    private function identificador(string $nombre): string {
        if (!preg_match('/^[A-Za-z_][A-Za-z0-9_]*$/', $nombre)) {
            throw new InvalidArgumentException('Identificador SQL no válido');
        }
        return '"' . $nombre . '"';
    }

    public function dameDatos(string $tabla): array {
        $tabla = $this->identificador($tabla);
        return $this->bd->query("SELECT * FROM $tabla")->fetchAll();
    }

    public function dameRegistro(string $tabla, string $pk, mixed $id): array {
        $tabla = $this->identificador($tabla);
        $pk = $this->identificador($pk);
        $st = $this->bd->prepare("SELECT * FROM $tabla WHERE $pk = :id LIMIT 1");
        $st->execute([':id' => $id]);
        return $st->fetch() ?: [];
    }

    public function dameCampos(string $tabla): array {
        $tablaSQL = $this->identificador($tabla);
        return $this->bd->query("PRAGMA table_info($tablaSQL)")->fetchAll();
    }

    public function dameClavePrimaria(string $tabla): ?string {
        foreach ($this->dameCampos($tabla) as $campo) {
            if ((int)$campo['pk'] === 1) return $campo['name'];
        }
        return null;
    }

    public function insertaDatos(string $tabla, array $datos): void {
        $campos = $this->dameCampos($tabla);
        $permitidos = array_column($campos, 'name');
        $pk = $this->dameClavePrimaria($tabla);
        $filtrados = [];
        foreach ($datos as $campo => $valor) {
            if (!in_array($campo, $permitidos, true)) continue;
            if ($campo === $pk && $valor === '') continue;
            $filtrados[$campo] = $valor;
        }
        if (!$filtrados) throw new RuntimeException('No hay datos para insertar');

        $cols = array_map(fn($c) => $this->identificador($c), array_keys($filtrados));
        $marks = array_map(fn($c) => ':' . $c, array_keys($filtrados));
        $tablaSQL = $this->identificador($tabla);
        $st = $this->bd->prepare("INSERT INTO $tablaSQL (".implode(',', $cols).") VALUES (".implode(',', $marks).")");
        foreach ($filtrados as $campo => $valor) $st->bindValue(':'.$campo, $valor);
        $st->execute();
    }

    public function actualizaDatos(string $tabla, string $pk, mixed $id, array $datos): void {
        $permitidos = array_column($this->dameCampos($tabla), 'name');
        $filtrados = [];
        foreach ($datos as $campo => $valor) {
            if ($campo !== $pk && in_array($campo, $permitidos, true)) $filtrados[$campo] = $valor;
        }
        if (!$filtrados) return;
        $sets = array_map(fn($c) => $this->identificador($c).' = :'.$c, array_keys($filtrados));
        $tablaSQL = $this->identificador($tabla);
        $pkSQL = $this->identificador($pk);
        $st = $this->bd->prepare("UPDATE $tablaSQL SET ".implode(',', $sets)." WHERE $pkSQL = :__pk");
        foreach ($filtrados as $campo => $valor) $st->bindValue(':'.$campo, $valor);
        $st->bindValue(':__pk', $id);
        $st->execute();
    }

    public function eliminaDatos(string $tabla, string $pk, mixed $id): void {
        $tablaSQL = $this->identificador($tabla);
        $pkSQL = $this->identificador($pk);
        $st = $this->bd->prepare("DELETE FROM $tablaSQL WHERE $pkSQL = :id");
        $st->execute([':id' => $id]);
    }

    public function autentica(string $usuario, string $contrasena): ?array {
        $st = $this->bd->prepare('SELECT * FROM usuarios WHERE usuario = :usuario AND contrasena = :contrasena LIMIT 1');
        $st->execute([':usuario' => $usuario, ':contrasena' => md5($contrasena)]);
        $fila = $st->fetch();
        return $fila ?: null;
    }

    public function dameTablasRol(mixed $rol): array {
        $st = $this->bd->prepare('SELECT tabla FROM roles WHERE idrol = :rol');
        $st->execute([':rol' => $rol]);
        return array_column($st->fetchAll(), 'tabla');
    }
}
