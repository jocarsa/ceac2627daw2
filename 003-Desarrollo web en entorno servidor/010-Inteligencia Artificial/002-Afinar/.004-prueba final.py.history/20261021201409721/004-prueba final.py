import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

MODELO = 'Qwen/Qwen3-4B'
ADAPTADOR = 'modelo_qlora'
quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16, bnb_4bit_use_double_quant=True)
tokenizer = AutoTokenizer.from_pretrained(MODELO)
base = AutoModelForCausalLM.from_pretrained(MODELO, quantization_config=quant, device_map='auto', torch_dtype='auto')
model = PeftModel.from_pretrained(base, ADAPTADOR)
model.eval()
historial = []
print('Chat afinado. Escribe salir para terminar.')
while True:
    pregunta = input('\nTú: ').strip()
    if pregunta.lower() in ('salir', 'exit'):
        break
    if not pregunta:
        continue
    mensajes = historial + [{'role': 'user', 'content': pregunta}]
    entrada = tokenizer.apply_chat_template(mensajes, tokenize=True, add_generation_prompt=True, enable_thinking=False, return_tensors='pt').to(model.device)
    with torch.inference_mode():
        salida = model.generate(entrada, max_new_tokens=256, do_sample=False, pad_token_id=tokenizer.eos_token_id)
    respuesta = tokenizer.decode(salida[0][entrada.shape[-1]:], skip_special_tokens=True).strip()
    print('Qwen afinado:', respuesta)
    historial += [{'role': 'user', 'content': pregunta}, {'role': 'assistant', 'content': respuesta}]
    historial = historial[-12:]