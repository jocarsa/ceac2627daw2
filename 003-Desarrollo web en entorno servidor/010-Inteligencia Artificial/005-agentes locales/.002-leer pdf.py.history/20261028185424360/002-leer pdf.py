import fitz

pdf = fitz.open("archivo.pdf")

for pagina in pdf:
    print(pagina.get_text())

pdf.close()