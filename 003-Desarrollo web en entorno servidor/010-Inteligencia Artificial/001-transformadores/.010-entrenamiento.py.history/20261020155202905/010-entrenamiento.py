
from sentence_transformers import (
    SentenceTransformer,
    InputExample,
    losses
)
from torch.utils.data import DataLoader

modelo = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

ejemplos = [
    InputExample(texts=[
        "El perro corre",
        "Un cachorro está corriendo"
    ]),
    InputExample(texts=[
        "Estoy programando en Python",
        "Desarrollo aplicaciones con Python"
    ]),
    InputExample(texts=[
        "La base de datos almacena información",
        "Una base de datos guarda registros"
    ]),
    InputExample(texts=[
        "El profesor explica la lección",
        "El docente imparte una clase"
    ]),
    InputExample(texts=[
        "El alumno realiza un examen",
        "El estudiante responde una prueba"
    ])
]

cargador = DataLoader(
    ejemplos,
    shuffle=True,
    batch_size=2
)

perdida = losses.MultipleNegativesRankingLoss(modelo)

modelo.fit(
    train_objectives=[(cargador, perdida)],
    epochs=10,
    warmup_steps=0,
    show_progress_bar=True
)

modelo.save("mi-modelo-embeddings")

print("Modelo entrenado y guardado")
