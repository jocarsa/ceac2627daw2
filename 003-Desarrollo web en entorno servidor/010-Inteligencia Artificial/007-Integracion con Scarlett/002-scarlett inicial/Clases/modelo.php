<?php
require_once __DIR__ . '/JocarsaCSV.php';

class JocarsaModelo {
    private JocarsaCSV $bd;
    private string $basededatos;
    private array $clavesPrimarias;

    public function __construct(string $rutaDatos, string $basededatos, array $clavesPrimarias = []) {
        $this->bd = new JocarsaCSV($rutaDatos);
        $this->basededatos = $basededatos;
        $this->clavesPrimarias = $clavesPrimarias;
    }

    private function validaNombre(string $nombre): string {
        if (!preg_match('/^[A-Za-z_][A-Za-z0-9_]*$/', $nombre)) throw new InvalidArgumentException('Nombre no válido');
        return $nombre;
    }

    private function rutaTabla(string $tabla): string {
        $tabla=$this->validaNombre($tabla);
        $ref=new ReflectionClass($this->bd); $prop=$ref->getProperty('rutaBase'); $prop->setAccessible(true);
        return rtrim($prop->getValue($this->bd),'/').'/'.$this->basededatos.'/'.$tabla.'.csv';
    }

    public function dameDatos(string $tabla): array { return $this->bd->listar($this->basededatos,$this->validaNombre($tabla)); }

    public function dameRegistro(string $tabla, string $pk, mixed $id): array {
        $r=$this->bd->buscar($this->basededatos,$this->validaNombre($tabla),$this->validaNombre($pk),$id);
        return $r[0] ?? [];
    }

    public function dameCampos(string $tabla): array {
        $ruta=$this->rutaTabla($tabla); if(!file_exists($ruta)) return [];
        $f=fopen($ruta,'r'); $cab=fgetcsv($f) ?: []; fclose($f); $pk=$this->dameClavePrimaria($tabla);
        return array_map(fn($n)=>['name'=>$n,'type'=>'TEXT','notnull'=>0,'dflt_value'=>null,'pk'=>$n===$pk?1:0],$cab);
    }

    public function dameClavePrimaria(string $tabla): ?string { return $this->clavesPrimarias[$tabla] ?? null; }

    private function siguienteId(string $tabla, string $pk): int {
        $max=0; foreach($this->dameDatos($tabla) as $fila) $max=max($max,(int)($fila[$pk]??0)); return $max+1;
    }

    public function insertaDatos(string $tabla, array $datos): void {
        $permitidos=array_column($this->dameCampos($tabla),'name'); $pk=$this->dameClavePrimaria($tabla); $fila=[];
        foreach($permitidos as $c) $fila[$c]=$datos[$c]??'';
        if($pk && ($fila[$pk]??'')==='') $fila[$pk]=$this->siguienteId($tabla,$pk);
        if(!$this->bd->insertar($this->basededatos,$tabla,$fila)) throw new RuntimeException('No se pudo insertar');
    }

    public function actualizaDatos(string $tabla,string $pk,mixed $id,array $datos): void {
        unset($datos[$pk]); $this->bd->actualizar($this->basededatos,$tabla,$pk,$id,$datos);
    }

    public function eliminaDatos(string $tabla,string $pk,mixed $id): void { $this->bd->eliminar($this->basededatos,$tabla,$pk,$id); }

    public function autentica(string $usuario,string $contrasena): ?array {
        foreach($this->bd->buscar($this->basededatos,'usuarios','usuario',$usuario) as $fila)
            if(($fila['contrasena']??'')===md5($contrasena)) return $fila;
        return null;
    }

    public function dameTablasRol(mixed $rol): array {
        $filas=$this->bd->buscar($this->basededatos,'roles','idrol',$rol);
        return array_values(array_unique(array_column($filas,'tabla')));
    }
}
