<?php
declare(strict_types=1);
function jocarsa_db(): PDO {
 $path=__DIR__.'/ialocal.db';
 if (!is_dir(__DIR__) || !is_writable(__DIR__) && !is_file($path)) throw new RuntimeException('La carpeta data debe permitir crear ialocal.db');
 $db=new PDO('sqlite:'.$path,null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC,PDO::ATTR_TIMEOUT=>5]);
 $db->exec('PRAGMA foreign_keys=ON');
 $db->exec("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT UNIQUE, contrasena TEXT, nombre TEXT, apellidos TEXT, email TEXT, id_empresa INTEGER, rol TEXT NOT NULL DEFAULT 'usuario')");
 $columns=array_column($db->query('PRAGMA table_info(usuarios)')->fetchAll(),'name');
 if (!in_array('rol',$columns,true)) $db->exec("ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT 'usuario'");
 $db->exec('CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_usuario ON usuarios(usuario)');
 $db->exec('CREATE TABLE IF NOT EXISTS conversaciones (id INTEGER PRIMARY KEY, titulo TEXT, fecha TEXT, id_usuario INTEGER)');
 $db->exec('CREATE TABLE IF NOT EXISTS mensajes (id INTEGER PRIMARY KEY, mensaje TEXT, emisor TEXT, fecha TEXT, id_conversacion INTEGER)');
 $db->exec('CREATE INDEX IF NOT EXISTS idx_conv_usuario ON conversaciones(id_usuario)');
 $db->exec('CREATE INDEX IF NOT EXISTS idx_msg_conv ON mensajes(id_conversacion,id)');
 $sql=<<<'SQL'
CREATE TABLE IF NOT EXISTS almacenes(id INTEGER PRIMARY KEY,nombre TEXT,direccion TEXT,ciudad TEXT);
CREATE TABLE IF NOT EXISTS categorias(id INTEGER PRIMARY KEY,nombre TEXT NOT NULL,descripcion TEXT);
CREATE TABLE IF NOT EXISTS clientes(Identificador INTEGER PRIMARY KEY,nombre TEXT NOT NULL,apellidos TEXT,telefono TEXT,email TEXT,direccion TEXT,ciudad TEXT,provincia TEXT,codigo_postal TEXT);
CREATE TABLE IF NOT EXISTS empleados(Identificador INTEGER PRIMARY KEY,nombre TEXT NOT NULL,apellidos TEXT,email TEXT,telefono TEXT,puesto TEXT,salario REAL,fecha_alta TEXT);
CREATE TABLE IF NOT EXISTS proveedores(id INTEGER PRIMARY KEY,nombre TEXT NOT NULL,contacto TEXT,telefono TEXT,email TEXT,ciudad TEXT);
CREATE TABLE IF NOT EXISTS productos(id INTEGER PRIMARY KEY,nombre TEXT NOT NULL,precio REAL,stock INTEGER,categoria_id INTEGER REFERENCES categorias(id),proveedor_id INTEGER REFERENCES proveedores(id));
CREATE TABLE IF NOT EXISTS pedidos(id INTEGER PRIMARY KEY,fecha TEXT,cliente_id INTEGER REFERENCES clientes(Identificador),empleado_id INTEGER REFERENCES empleados(Identificador),estado TEXT,total REAL);
CREATE TABLE IF NOT EXISTS facturas(id INTEGER PRIMARY KEY,numero TEXT,pedido_id INTEGER REFERENCES pedidos(id),fecha TEXT,base_imponible REAL,iva REAL,total REAL,estado TEXT);
CREATE TABLE IF NOT EXISTS inventario(id INTEGER PRIMARY KEY,almacen_id INTEGER REFERENCES almacenes(id),producto_id INTEGER REFERENCES productos(id),unidades INTEGER,ubicacion TEXT);
CREATE TABLE IF NOT EXISTS lineas_pedido(id INTEGER PRIMARY KEY,pedido_id INTEGER REFERENCES pedidos(id),producto_id INTEGER REFERENCES productos(id),cantidad INTEGER,precio_unitario REAL);
CREATE TABLE IF NOT EXISTS pagos(id INTEGER PRIMARY KEY,factura_id INTEGER REFERENCES facturas(id),fecha TEXT,importe REAL,metodo TEXT,referencia TEXT);
SQL;
 $db->exec($sql);
 return $db;
}
