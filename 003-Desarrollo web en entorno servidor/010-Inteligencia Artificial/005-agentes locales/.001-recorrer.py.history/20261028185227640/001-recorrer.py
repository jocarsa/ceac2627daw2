import os

for raiz, carpetas, archivos in os.walk("/home/josevicente/Escritorio"):
    for archivo in archivos:
        if archivo.lower().endswith(".pdf"):
            ruta = os.path.join(raiz, archivo)
            print(ruta)