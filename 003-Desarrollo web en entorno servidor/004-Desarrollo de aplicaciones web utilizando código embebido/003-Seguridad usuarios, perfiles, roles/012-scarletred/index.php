<?php
session_start();
include "includes/principio.php";
?>
<?php if(isset($_SESSION['llave'])){ ?>
<header>
  <div class="marca"><strong>ScarletRed</strong><span>Panel de administración</span></div>
  <div class="usuario"><span><?php echo htmlspecialchars($_SESSION['nombre'] ?? 'Usuario'); ?></span><a href="matarsesion.php">Cerrar sesión</a></div>
</header>
<main>
  <nav>
    <div class="nav-titulo">Administración</div>
    <?php include "includes/navegacion.php"; ?>
  </nav>
  <section>
    <?php
      $tabla = isset($_GET['tabla']) ? $_GET['tabla'] : "clientes";
      $accion = isset($_GET['accion']) ? $_GET['accion'] : "listar";
    ?>
    <div class="titulo-pagina">
      <div><h1><?php echo htmlspecialchars(ucfirst($tabla)); ?></h1><p>Gestiona los registros de <?php echo htmlspecialchars($tabla); ?>.</p></div>
      <?php if($accion === "listar"){ ?>
        <a class="boton boton-primario" href="?tabla=<?php echo urlencode($tabla); ?>&accion=nuevo">Añadir nuevo</a>
      <?php }else{ ?>
        <a class="boton" href="?tabla=<?php echo urlencode($tabla); ?>">← Volver al listado</a>
      <?php } ?>
    </div>
    <?php
      if($accion === "nuevo" || $accion === "editar"){
        include "includes/formulario.php";
      }else{
        include "includes/tabla.php";
      }
    ?>
  </section>
</main>
<?php }else{ include "includes/login.php"; } ?>
<?php include "includes/final.php"; ?>
