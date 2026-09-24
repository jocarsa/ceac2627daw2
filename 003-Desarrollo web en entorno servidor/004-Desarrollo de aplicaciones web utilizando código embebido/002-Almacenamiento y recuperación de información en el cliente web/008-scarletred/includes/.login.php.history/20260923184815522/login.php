<!doctype html>
<html>
  <head>
    <style>
      body{
        font-family:Arial;
        background:#f0f0f1;
      }
      form{
        width:300px;
        margin:100px auto;
        padding:20px;
        background:white;
      }
      input{
        width:100%;
        padding:10px;
        margin:5px 0;
        box-sizing:border-box;
      }
    </style>
  </head>
  <body>
    <form method="POST" action="login.php">
      <input type="text" name="usuario" placeholder="Usuario">
      <input type="password" name="contrasena" placeholder="Contraseña">
      <input type="submit" value="Entrar">
    </form>
  </body>
</html>