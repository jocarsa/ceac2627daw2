import fitz

pdf = fitz.open("/home/josevicente/Escritorio/informe_alumnos_seleccionados_2026-10-28.pdf")

for pagina in pdf:
    print(pagina.get_text())

pdf.close()