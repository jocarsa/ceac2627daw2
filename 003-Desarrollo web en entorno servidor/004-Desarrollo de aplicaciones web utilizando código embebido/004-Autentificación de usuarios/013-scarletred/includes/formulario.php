<?php
$db = new SQLite3('empresa.db');
$info = $db->query("PRAGMA table_info(".$tabla.")");
$campos=[]; $pk=null;
while($c=$info->fetchArray(SQLITE3_ASSOC)){ $campos[]=$c; if($c['pk']==1) $pk=$c['name']; }
$editando = $accion === "editar";
$datos=[];
if($editando && isset($_GET['id']) && $pk){
    $st=$db->prepare("SELECT * FROM ".$tabla." WHERE ".$pk."=:id");
    $st->bindValue(':id',$_GET['id']); $r=$st->execute();
    $datos=$r->fetchArray(SQLITE3_ASSOC) ?: [];
}
if(isset($_POST['insertar'])){
    $cols=[];$marks=[];
    foreach($campos as $c){
        $n=$c['name'];
        if($c['pk']==1 && ($_POST[$n]??'')==='') continue;
        $cols[]=$n;$marks[]=':'.$n;
    }
    $st=$db->prepare("INSERT INTO ".$tabla." (".implode(',',$cols).") VALUES (".implode(',',$marks).")");
    foreach($cols as $n) $st->bindValue(':'.$n,$_POST[$n]??'');
    $st->execute(); header("Location:?tabla=".urlencode($tabla)); exit();
}
if(isset($_POST['actualizar']) && $pk){
    $sets=[];
    foreach($campos as $c) if($c['name']!==$pk) $sets[]=$c['name'].'=:'.$c['name'];
    $st=$db->prepare("UPDATE ".$tabla." SET ".implode(',',$sets)." WHERE ".$pk."=:pk");
    foreach($campos as $c) if($c['name']!==$pk) $st->bindValue(':'.$c['name'],$_POST[$c['name']]??'');
    $st->bindValue(':pk',$_POST[$pk]); $st->execute();
    header("Location:?tabla=".urlencode($tabla)); exit();
}
?>
<div class="caja formulario-caja">
<h2><?php echo $editando ? "Editar registro" : "Añadir nuevo registro"; ?></h2>
<form method="POST">
<?php foreach($campos as $c){ $n=$c['name']; $v=$datos[$n]??''; ?>
<div class="campo">
<label><?php echo htmlspecialchars(ucfirst($n)); ?></label>
<input type="text" name="<?php echo htmlspecialchars($n); ?>" value="<?php echo htmlspecialchars($v); ?>" <?php echo ($editando && $n===$pk)?'readonly':''; ?>>
</div>
<?php } ?>
<input class="boton boton-primario" type="submit" name="<?php echo $editando?'actualizar':'insertar'; ?>" value="<?php echo $editando?'Actualizar':'Añadir registro'; ?>">
</form>
</div>
<?php $db->close(); ?>
