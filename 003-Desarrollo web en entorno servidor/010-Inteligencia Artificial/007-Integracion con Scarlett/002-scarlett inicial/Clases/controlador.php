<?php
class JocarsaControlador {
    private JocarsaModelo $modelo;

    public function __construct(JocarsaModelo $modelo) {
        $this->modelo = $modelo;
    }

    public function login(string $usuario, string $contrasena): bool {
        $fila = $this->modelo->autentica($usuario, $contrasena);
        if (!$fila) return false;
        session_regenerate_id(true);
        $_SESSION['llave'] = 'jocarsa';
        $_SESSION['rol'] = $fila['rol'];
        $_SESSION['nombre'] = $fila['nombre'];
        return true;
    }

    public function logout(): void {
        $_SESSION = [];
        if (ini_get('session.use_cookies')) {
            $p = session_get_cookie_params();
            setcookie(session_name(), '', time()-42000, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
        }
        session_destroy();
    }

    public function tablasPermitidas(): array {
        return $this->modelo->dameTablasRol($_SESSION['rol'] ?? '');
    }

    public function tablaSolicitada(): string {
        $permitidas = $this->tablasPermitidas();
        $tabla = $_GET['tabla'] ?? ($permitidas[0] ?? 'clientes');
        if (!in_array($tabla, $permitidas, true)) $tabla = $permitidas[0] ?? 'clientes';
        return $tabla;
    }

    public function procesaCrud(string $tabla): array {
        $accion = $_GET['accion'] ?? 'listar';
        $campos = $this->modelo->dameCampos($tabla);
        $pk = $this->modelo->dameClavePrimaria($tabla);

        if (isset($_GET['eliminar']) && $pk) {
            $this->modelo->eliminaDatos($tabla, $pk, $_GET['eliminar']);
            $this->redirigeTabla($tabla);
        }
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['insertar'])) {
            $datos = $_POST; unset($datos['insertar']);
            $this->modelo->insertaDatos($tabla, $datos);
            $this->redirigeTabla($tabla);
        }
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['actualizar']) && $pk) {
            $datos = $_POST; unset($datos['actualizar']);
            $id = $datos[$pk] ?? null;
            $this->modelo->actualizaDatos($tabla, $pk, $id, $datos);
            $this->redirigeTabla($tabla);
        }

        $registro = [];
        if ($accion === 'editar' && isset($_GET['id']) && $pk) {
            $registro = $this->modelo->dameRegistro($tabla, $pk, $_GET['id']);
        }
        return [
            'tabla' => $tabla,
            'accion' => $accion,
            'campos' => $campos,
            'pk' => $pk,
            'registro' => $registro,
            'datos' => $accion === 'listar' ? $this->modelo->dameDatos($tabla) : []
        ];
    }

    private function redirigeTabla(string $tabla): never {
        header('Location:index.php?tabla='.urlencode($tabla));
        exit();
    }
}