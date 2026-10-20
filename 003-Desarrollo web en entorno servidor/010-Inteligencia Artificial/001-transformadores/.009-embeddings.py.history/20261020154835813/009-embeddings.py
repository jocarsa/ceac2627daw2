
from sentence_transformers import SentenceTransformer

# Cargar modelo multilingüe
modelo = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

frases = [
    "El perro está jugando",
    "Un cachorro corre por el parque",
    "El gato está durmiendo",
    "Estoy programando en Python",
    "Me gusta desarrollar software",
    "La base de datos contiene registros"
]

embeddings = modelo.encode(frases)

for frase, vector in zip(frases, embeddings):
    print("\nFrase:", frase)
    print("Dimensiones:", len(vector))
    print("Primeros valores:", vector[:10])
