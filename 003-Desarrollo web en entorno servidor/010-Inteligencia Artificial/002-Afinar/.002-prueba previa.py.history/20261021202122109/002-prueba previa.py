
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)

# ----------------------------------------
# 1. Configuración
# ----------------------------------------

MODELO = "Qwen/Qwen3-4B"
MAX_TOKENS = 256

# ----------------------------------------
# 2. Cuantización 4 bits
# ----------------------------------------

tipo = (
    torch.bfloat16
    if torch.cuda.is_bf16_supported()
    else torch.float16
)

quant = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=tipo,
    bnb_4bit_use_double_quant=True
)

# ----------------------------------------
# 3. Cargar modelo
# ----------------------------------------

print("Cargando tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(MODELO)

print("Cargando modelo...")

model = AutoModelForCausalLM.from_pretrained(
    MODELO,
    quantization_config=quant,
    device_map="auto",
    torch_dtype="auto"
)

model.eval()

print("Modelo cargado correctamente.")

# ----------------------------------------
# 4. Historial
# ----------------------------------------

historial = []

print("\nChat original (sin fine-tuning)")
print("Escribe 'salir' para terminar.")

# ----------------------------------------
# 5. Chat
# ----------------------------------------

while True:

    pregunta = input("\nTú: ").strip()

    if pregunta.lower() in ("salir", "exit"):
        break

    if not pregunta:
        continue

    mensajes = historial + [
        {
            "role": "user",
            "content": pregunta
        }
    ]

    # Crear entrada correctamente
    entrada = tokenizer.apply_chat_template(
        mensajes,
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=False,
        return_tensors="pt",
        return_dict=True
    )

    # Mover tensores al dispositivo
    entrada = {
        clave: valor.to(model.device)
        for clave, valor in entrada.items()
    }

    longitud_entrada = entrada["input_ids"].shape[-1]

    # Generar respuesta
    with torch.inference_mode():

        salida = model.generate(
            **entrada,
            max_new_tokens=MAX_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    # Extraer únicamente los tokens nuevos
    nuevos_tokens = salida[0][longitud_entrada:]

    respuesta = tokenizer.decode(
        nuevos_tokens,
        skip_special_tokens=True
    ).strip()

    print("\nQwen:", respuesta)

    # Guardar conversación
    historial.append({
        "role": "user",
        "content": pregunta
    })

    historial.append({
        "role": "assistant",
        "content": respuesta
    })

    # Mantener últimas 12 intervenciones
    historial = historial[-12:]

print("\nChat finalizado.")
