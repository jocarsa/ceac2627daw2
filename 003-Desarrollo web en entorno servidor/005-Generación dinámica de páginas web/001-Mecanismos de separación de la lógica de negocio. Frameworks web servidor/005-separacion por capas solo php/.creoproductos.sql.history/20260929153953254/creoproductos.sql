CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    categoria TEXT,
    precio REAL NOT NULL,
    stock INTEGER DEFAULT 0,
    marca TEXT,
    activo INTEGER DEFAULT 1,
    fecha_alta TEXT DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO productos
(nombre, descripcion, categoria, precio, stock, marca, activo)
VALUES
('Portátil Lenovo IdeaPad', 'Portátil de 15 pulgadas con 16 GB de RAM', 'Informática', 749.99, 12, 'Lenovo', 1),

('Ratón Logitech M185', 'Ratón inalámbrico USB', 'Periféricos', 19.95, 45, 'Logitech', 1),

('Teclado mecánico K2', 'Teclado mecánico con iluminación LED', 'Periféricos', 79.90, 18, 'Keychron', 1),

('Monitor 27 pulgadas', 'Monitor IPS Full HD de 27 pulgadas', 'Monitores', 189.99, 9, 'LG', 1),

('Disco SSD 1TB', 'Unidad SSD NVMe de 1 TB', 'Almacenamiento', 89.50, 27, 'Kingston', 1),

('Memoria RAM 16GB', 'Módulo DDR4 de 16 GB', 'Componentes', 42.99, 35, 'Crucial', 1),

('Tarjeta gráfica RTX 4060', 'Tarjeta gráfica con 8 GB de memoria', 'Componentes', 329.00, 7, 'Gigabyte', 1),

('Auriculares inalámbricos', 'Auriculares Bluetooth con micrófono', 'Audio', 59.95, 22, 'Sony', 1),

('Webcam Full HD', 'Webcam USB 1080p con micrófono', 'Periféricos', 39.99, 14, 'Logitech', 1),

('Hub USB-C', 'Hub USB-C con HDMI y cuatro puertos USB', 'Accesorios', 34.90, 31, 'Anker', 1),

('Cable HDMI 2m', 'Cable HDMI de alta velocidad', 'Accesorios', 9.95, 120, 'Amazon Basics', 1),

('Impresora láser', 'Impresora láser monocromo con WiFi', 'Impresoras', 159.00, 5, 'Brother', 1),

('Tablet 10 pulgadas', 'Tablet Android con 128 GB de almacenamiento', 'Tablets', 249.99, 11, 'Samsung', 1),

('Altavoz Bluetooth', 'Altavoz portátil resistente al agua', 'Audio', 49.90, 26, 'JBL', 1),

('Router WiFi 6', 'Router inalámbrico compatible con WiFi 6', 'Redes', 89.99, 16, 'TP-Link', 1),

('Switch 8 puertos', 'Switch Gigabit Ethernet de 8 puertos', 'Redes', 29.95, 23, 'TP-Link', 1),

('Fuente alimentación 750W', 'Fuente modular de 750 vatios', 'Componentes', 109.90, 8, 'Corsair', 1),

('Caja ATX', 'Caja ATX con lateral de cristal templado', 'Componentes', 74.50, 13, 'NZXT', 1),

('Micrófono USB', 'Micrófono USB para streaming y videoconferencia', 'Audio', 69.99, 17, 'HyperX', 1),

('Producto descatalogado', 'Producto antiguo fuera de catálogo', 'Otros', 15.00, 0, 'Genérica', 0);