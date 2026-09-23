<?php
$db=new SQLite3('empresa.db');
$info=$db->query("PRAGMA table_info(".$tabla.")"); $campos=[];$pk=null;
while($c=$info->fetchArray(SQLITE3_ASSOC)){ $campos[]=$c['name']; if($c['pk']==1)$pk=$c['name']; }
if(isset($_GET['eliminar']) && $pk){
    $st=$db->prepare("DELETE FROM ".$tabla." WHERE ".$pk."=:id");
    $st->bindValue(':id',$_GET['eliminar']); $st->execute();
    header("Location:?tabla=".urlencode($tabla)); exit();
}
$result=$db->query("SELECT * FROM ".$tabla);
?>
<div class="caja tabla-contenedor">
<table>
<thead><tr>
<?php foreach($campos as $c) echo "<th>".htmlspecialchars(ucfirst($c))."</th>"; ?>
<th>Acciones</th></tr></thead>
<tbody>
<?php while($fila=$result->fetchArray(SQLITE3_ASSOC)){ ?>
<tr>
<?php foreach($campos as $c){ ?><td><?php echo htmlspecialchars($fila[$c]??''); ?></td><?php } ?>
<td class="acciones">
<?php if($pk){ $id=urlencode($fila[$pk]); ?>
<a href="?tabla=<?php echo urlencode($tabla); ?>&accion=editar&id=<?php echo $id; ?>">Editar</a>
<a class="eliminar" onclick="return confirm('¿Seguro que quieres eliminar este registro?')" href="?tabla=<?php echo urlencode($tabla); ?>&eliminar=<?php echo $id; ?>">Eliminar</a>
<?php } ?>
</td></tr>
<?php } ?>
</tbody></table>
</div>
<?php $db->close(); ?>
