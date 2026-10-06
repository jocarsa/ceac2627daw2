<div class="login-pantalla">
  <div class="login-caja">
    <div class="login-logo">S</div>
    <h1>ScarletRed</h1>
    <p>Panel de administración</p>
    <?php if(isset($_GET['error'])){ ?><div class="aviso-error">Usuario o contraseña incorrectos.</div><?php } ?>
    <form method="POST" action="login.php">
      <label>Usuario</label>
      <input type="text" name="usuario" autocomplete="username" required>
      <label>Contraseña</label>
      <input type="password" name="contrasena" autocomplete="current-password" required>
      <input class="boton boton-primario boton-login" type="submit" value="Acceder">
    </form>
  </div>
</div>
