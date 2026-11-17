<?php
class JocarsaVista {
    private array $config;

    public function __construct(array $config = []) {
        $this->config = $config;
    }

    private function h(mixed $v): string { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); }

    public function principio(?string $titulo=null): void {
        $titulo = $titulo ?? ($this->config['nombre'] ?? 'ScarletRed'); ?>
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title><?= $this->h($titulo) ?></title><link rel="stylesheet" href="css/estilo.css"><style>:root{--rojo:<?= $this->h($this->config['color'] ?? '#b32d2e') ?>;--colorcorporativo:<?= $this->h($this->config['color'] ?? '#b32d2e') ?>}</style></head><body>
<?php }

    public function final(): void { echo '</body></html>'; }

    public function login(bool $error=false): void { ?>
<div class="login-pantalla"><div class="login-caja"><div class="login-logo"><?= $this->h($this->config['logo'] ?? 'S') ?></div><h1><?= $this->h($this->config['nombre'] ?? 'ScarletRed') ?></h1><p><?= $this->h($this->config['subtitulo'] ?? 'Panel de administración') ?></p>
<?php if($error): ?><div class="aviso-error">Usuario o contraseña incorrectos.</div><?php endif; ?>
<form method="POST" action="login.php"><label>Usuario</label><input type="text" name="usuario" autocomplete="username" required>
<label>Contraseña</label><input type="password" name="contrasena" autocomplete="current-password" required>
<input class="boton boton-primario boton-login" type="submit" value="Acceder"></form></div></div><?php
    }

    public function abrePanel(string $nombre, array $tablas, string $tabla, string $accion): void { ?>
<header><div class="marca"><strong><?= $this->h($this->config['nombre'] ?? 'ScarletRed') ?></strong><span><?= $this->h($this->config['subtitulo'] ?? 'Panel de administración') ?></span></div><div class="usuario"><span><?= $this->h($nombre) ?></span><a href="matarsesion.php">Cerrar sesión</a></div></header>
<main><nav><div class="nav-titulo">Administración</div><?php foreach($tablas as $t): ?><a class="nav-link" href="?tabla=<?= urlencode($t) ?>"><?= $this->h(ucfirst($t)) ?></a><?php endforeach; ?></nav><section>
<div class="titulo-pagina"><div><h1><?= $this->h(ucfirst($tabla)) ?></h1><p>Gestiona los registros de <?= $this->h($tabla) ?>.</p></div>
<?php if($accion==='listar'): ?><a class="boton boton-primario" href="?tabla=<?= urlencode($tabla) ?>&accion=nuevo">Añadir nuevo</a><?php else: ?><a class="boton" href="?tabla=<?= urlencode($tabla) ?>">← Volver al listado</a><?php endif; ?></div><?php
    }

    public function cierraPanel(): void { echo '</section></main>'; }

    public function pintaTabla(array $datos, array $campos, ?string $pk, string $tabla): void { ?>
<div class="caja tabla-contenedor"><table><thead><tr><?php foreach($campos as $c): if ($c['name']==='contrasena') continue; ?><th><?= $this->h(ucfirst($c['name'])) ?></th><?php endforeach; ?><th>Acciones</th></tr></thead><tbody>
<?php foreach($datos as $fila): ?><tr><?php foreach($campos as $c): $n=$c['name']; if ($n==='contrasena') continue; ?><td><?= $this->h($fila[$n] ?? '') ?></td><?php endforeach; ?><td class="acciones">
<?php if($pk): $id=urlencode((string)$fila[$pk]); ?><a href="?tabla=<?= urlencode($tabla) ?>&accion=editar&id=<?= $id ?>">Editar</a><form method="post" style="display:inline" onsubmit="return confirm('¿Eliminar este registro?')"><input type="hidden" name="csrf_admin" value="<?= $this->h($_SESSION['csrf_admin']) ?>"><input type="hidden" name="eliminar" value="<?= $this->h($fila[$pk]) ?>"><button type="submit">Eliminar</button></form><?php endif; ?></td></tr><?php endforeach; ?>
</tbody></table></div><?php
    }

    public function pintaFormulario(array $campos, array $registro, ?string $pk, string $accion): void {
        $editando = $accion === 'editar'; ?>
<div class="caja formulario-caja"><h2><?= $editando ? 'Editar registro' : 'Añadir nuevo registro' ?></h2><form method="POST"><input type="hidden" name="csrf_admin" value="<?= $this->h($_SESSION['csrf_admin']) ?>">
<?php foreach($campos as $c): $n=$c['name']; $v=$registro[$n]??''; ?><div class="campo"><label><?= $this->h(ucfirst($n)) ?></label><input type="<?= $n==='contrasena'?'password':'text' ?>" name="<?= $this->h($n) ?>" value="<?= $n==='contrasena'?'':$this->h($v) ?>" placeholder="<?= $n==='contrasena'&&$editando?'Dejar vacío para mantener contraseña':'' ?>" <?= ($editando && $n===$pk)?'readonly':'' ?>></div><?php endforeach; ?>
<input class="boton boton-primario" type="submit" name="<?= $editando?'actualizar':'insertar' ?>" value="<?= $editando?'Actualizar':'Añadir registro' ?>"></form></div><?php
    }
}
