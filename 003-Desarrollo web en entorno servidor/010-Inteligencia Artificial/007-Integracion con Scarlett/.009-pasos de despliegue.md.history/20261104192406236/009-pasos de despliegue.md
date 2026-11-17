1.-Acceder al proveedor de dominios
2.-Crear dos subdominios para el proyecto

3.-Ahora esperamos 10-15

4.-en el servidor, creamos una carpeta de destino
(ftp, ssh, etc)
5.-desde el cliente, subimos el proyecto
(ftp, ssh, etc)

6.-Ahora en el servidor tengo que crear un par de virtualhosts
Le dice al servidor en qué carpeta está qué dominio
.creo un config en /etc/apache2/sites-available

cd /etc/apache2/sites-available
sudo nano ia.jocarsa.com.conf
sudo nano iaadmin.jocarsa.com.conf

7.-Activamos los virtualhosts
sudo a2ensite ia.jocarsa.com.conf
sudo a2ensite iaadmin.jocarsa.com.conf

8.-Reiniciamos servidor
sudo service apache2 restart