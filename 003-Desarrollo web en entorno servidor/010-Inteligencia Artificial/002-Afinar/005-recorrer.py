import os

carpeta = "/var/www/html/clases/"

for raiz, carpetas, archivos in os.walk(carpeta):
    for archivo in archivos:
        if archivo.lower().endswith(".txt"):
            ruta = os.path.join(raiz, archivo)
            print(ruta)