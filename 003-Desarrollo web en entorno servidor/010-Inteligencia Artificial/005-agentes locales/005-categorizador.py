import os
import fitz

origen = "/home/josevicente/Escritorio"
destino = "/home/josevicente/Escritorio/todos_los_pdfs.txt"

with open(destino, "w", encoding="utf-8") as salida:

    for raiz, carpetas, archivos in os.walk(origen):
        for archivo in archivos:
            if archivo.lower().endswith(".pdf"):
                ruta = os.path.join(raiz, archivo)
                print("Procesando:", ruta)

                try:
                    with fitz.open(ruta) as pdf:
                        salida.write("\n\n" + "=" * 80 + "\n")
                        salida.write("ARCHIVO: " + ruta + "\n")
                        salida.write("=" * 80 + "\n\n")

                        for pagina in pdf:
                            salida.write(pagina.get_text())
                            salida.write("\n")

                except Exception as e:
                    print("Error:", e)

print("Todos los PDF acumulados en:", destino)