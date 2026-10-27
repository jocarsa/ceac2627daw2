
from sentence_transformers import SentenceTransformer
from sentence_transformers import util

modelo = SentenceTransformer("mi-modelo-embeddings")

documentos = [
    "Python es un lenguaje de programación",
    "MySQL es un sistema gestor de bases de datos",
    "HTML permite estructurar páginas web",
    "JavaScript permite programar interfaces web",
    "Un profesor evalúa a sus alumnos"
]

consulta = "¿Cómo puedo crear programas informáticos?"

vector_consulta = modelo.encode(consulta)
vectores = modelo.encode(documentos)

resultados = util.cos_sim(
    vector_consulta,
    vectores
)[0]

ordenados = sorted(
    zip(documentos, resultados),
    key=lambda x: x[1].item(),
    reverse=True
)

for documento, similitud in ordenados:
    print(
        round(similitud.item(), 3),
        documento
    )
