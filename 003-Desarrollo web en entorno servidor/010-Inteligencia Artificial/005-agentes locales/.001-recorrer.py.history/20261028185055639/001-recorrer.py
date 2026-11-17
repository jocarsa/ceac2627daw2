import os

for raiz, carpetas, archivos in os.walk("."):
    for archivo in archivos:
        if archivo.lower().endswith(".pdf"):
            ruta = os.path.join(raiz, archivo)
            print(ruta)