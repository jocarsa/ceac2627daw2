<?php
require_once __DIR__.'/config.php';
require_once __DIR__.'/Clases/JocarsaCSV.php';
$db=new JocarsaCSV($config['ruta_datos']); $base=$config['basededatos']; $db->crearBaseDatos($base);
$tablas=[
'usuarios'=>['Identificador','usuario','contrasena','nombre','rol'],
'roles'=>['Identificador','idrol','tabla'],
'clientes'=>['Identificador','nombre','apellidos','telefono','email','direccion','ciudad','provincia','codigo_postal'],
'empleados'=>['Identificador','nombre','apellidos','email','telefono','puesto','salario','fecha_alta'],
'categorias'=>['id','nombre','descripcion'], 'proveedores'=>['id','nombre','contacto','telefono','email','ciudad'],
'productos'=>['id','nombre','precio','stock','categoria_id','proveedor_id'], 'almacenes'=>['id','nombre','direccion','ciudad'],
'inventario'=>['id','almacen_id','producto_id','unidades','ubicacion'], 'pedidos'=>['id','fecha','cliente_id','empleado_id','estado','total'],
'lineas_pedido'=>['id','pedido_id','producto_id','cantidad','precio_unitario'], 'facturas'=>['id','numero','pedido_id','fecha','base_imponible','iva','total','estado'],
'pagos'=>['id','factura_id','fecha','importe','metodo','referencia']];
foreach($tablas as $t=>$cols) $db->crearTabla($base,$t,$cols);
function ins($db,$b,$t,$rows){foreach($rows as $r)$db->insertar($b,$t,$r);}
ins($db,$base,'usuarios',[
['Identificador'=>1,'usuario'=>'admin','contrasena'=>md5('admin123'),'nombre'=>'Administrador','rol'=>1],
['Identificador'=>2,'usuario'=>'ventas','contrasena'=>md5('ventas123'),'nombre'=>'Laura Ventas','rol'=>2]]);
$id=1; foreach(['clientes','empleados','categorias','proveedores','productos','almacenes','inventario','pedidos','lineas_pedido','facturas','pagos'] as $t){$roles[]=['Identificador'=>$id++,'idrol'=>1,'tabla'=>$t];}
foreach(['clientes','productos','pedidos','facturas'] as $t)$roles[]=['Identificador'=>$id++,'idrol'=>2,'tabla'=>$t]; ins($db,$base,'roles',$roles);
$nombres=['Ana','Carlos','Lucía','Miguel','Sofía','David','Elena','Pablo','Marta','Javier','Paula','Sergio']; $ap=['García','Martínez','López','Sánchez','Pérez','Gómez'];
$clientes=[]; for($i=1;$i<=30;$i++){$nom=$nombres[($i-1)%count($nombres)];$ape=$ap[($i-1)%count($ap)];$clientes[]=['Identificador'=>$i,'nombre'=>$nom,'apellidos'=>$ape,'telefono'=>'600'.str_pad($i,6,'0',STR_PAD_LEFT),'email'=>strtolower($nom).$i.'@ejemplo.test','direccion'=>'Calle '.($i+10).', '.$i,'ciudad'=>['Valencia','Torrent','Paterna','Burjassot','Mislata'][$i%5],'provincia'=>'Valencia','codigo_postal'=>(string)(46000+$i)];} ins($db,$base,'clientes',$clientes);
ins($db,$base,'empleados',[
['Identificador'=>1,'nombre'=>'Laura','apellidos'=>'Navarro','email'=>'laura@empresa.test','telefono'=>'610000001','puesto'=>'Ventas','salario'=>'24500','fecha_alta'=>'2023-02-01'],
['Identificador'=>2,'nombre'=>'Álvaro','apellidos'=>'Ruiz','email'=>'alvaro@empresa.test','telefono'=>'610000002','puesto'=>'Almacén','salario'=>'22800','fecha_alta'=>'2024-05-15'],
['Identificador'=>3,'nombre'=>'Nuria','apellidos'=>'Torres','email'=>'nuria@empresa.test','telefono'=>'610000003','puesto'=>'Administración','salario'=>'26000','fecha_alta'=>'2022-09-12']]);
ins($db,$base,'categorias',[[ 'id'=>1,'nombre'=>'Informática','descripcion'=>'Equipos y periféricos'],['id'=>2,'nombre'=>'Oficina','descripcion'=>'Material de oficina'],['id'=>3,'nombre'=>'Redes','descripcion'=>'Conectividad y redes']]);
ins($db,$base,'proveedores',[[ 'id'=>1,'nombre'=>'Levante Tech','contacto'=>'Raquel','telefono'=>'960100100','email'=>'ventas@levante.test','ciudad'=>'Valencia'],['id'=>2,'nombre'=>'Suministros Turia','contacto'=>'Andrés','telefono'=>'960200200','email'=>'info@turia.test','ciudad'=>'Paterna']]);
$prod=['Teclado mecánico','Ratón óptico','Monitor 24 pulgadas','SSD 1 TB','Cable HDMI 2m','Switch 8 puertos','Punto de acceso WiFi','Webcam Full HD','Auriculares USB','Hub USB-C','Cuaderno A4','Pack bolígrafos']; $rows=[]; foreach($prod as $i=>$n)$rows[]=['id'=>$i+1,'nombre'=>$n,'precio'=>number_format(8.5+($i*13.37),2,'.',''),'stock'=>20+$i*7,'categoria_id'=>$i<10?($i%3)+1:2,'proveedor_id'=>($i%2)+1]; ins($db,$base,'productos',$rows);
ins($db,$base,'almacenes',[[ 'id'=>1,'nombre'=>'Central','direccion'=>'Av. Industria 10','ciudad'=>'Valencia'],['id'=>2,'nombre'=>'Norte','direccion'=>'C/ Logística 22','ciudad'=>'Paterna']]);
$inv=[]; $iid=1; for($p=1;$p<=12;$p++)for($a=1;$a<=2;$a++)$inv[]=['id'=>$iid++,'almacen_id'=>$a,'producto_id'=>$p,'unidades'=>10+$p*$a,'ubicacion'=>'P'.$a.'-E'.ceil($p/3).'-B'.$p]; ins($db,$base,'inventario',$inv);
$ped=[];$lin=[];$fac=[];$pag=[];$lid=1; for($i=1;$i<=20;$i++){ $total=round(35+$i*17.25,2);$ped[]=['id'=>$i,'fecha'=>'2026-09-'.str_pad(($i%28)+1,2,'0',STR_PAD_LEFT),'cliente_id'=>(($i-1)%30)+1,'empleado_id'=>(($i-1)%3)+1,'estado'=>['pendiente','preparando','enviado','entregado'][$i%4],'total'=>$total]; $lin[]=['id'=>$lid++,'pedido_id'=>$i,'producto_id'=>(($i-1)%12)+1,'cantidad'=>1+($i%4),'precio_unitario'=>round($total/(1+($i%4)),2)]; $baseImp=round($total/1.21,2);$fac[]=['id'=>$i,'numero'=>'F-2026-'.str_pad($i,4,'0',STR_PAD_LEFT),'pedido_id'=>$i,'fecha'=>'2026-09-'.str_pad(($i%28)+1,2,'0',STR_PAD_LEFT),'base_imponible'=>$baseImp,'iva'=>round($total-$baseImp,2),'total'=>$total,'estado'=>$i%3?'pagada':'pendiente']; if($i%3)$pag[]=['id'=>count($pag)+1,'factura_id'=>$i,'fecha'=>'2026-09-'.str_pad((($i+1)%28)+1,2,'0',STR_PAD_LEFT),'importe'=>$total,'metodo'=>['tarjeta','transferencia','bizum'][$i%3],'referencia'=>'PAGO-'.$i]; }
ins($db,$base,'pedidos',$ped);ins($db,$base,'lineas_pedido',$lin);ins($db,$base,'facturas',$fac);ins($db,$base,'pagos',$pag);
echo '<h1>Importación terminada</h1><p>Base CSV creada en <code>datos/empresa/</code>.</p><p>Usuario: <b>admin</b> / contraseña: <b>admin123</b></p><p><a href="index.php">Entrar en ScarletRed</a></p>';
