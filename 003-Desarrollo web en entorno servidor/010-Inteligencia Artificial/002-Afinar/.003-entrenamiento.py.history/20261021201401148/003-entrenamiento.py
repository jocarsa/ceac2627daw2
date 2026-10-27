import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer

MODELO = 'Qwen/Qwen3-4B'
DATOS = 'entrenamiento.jsonl'
SALIDA = 'modelo_qlora'

if not torch.cuda.is_available():
    raise RuntimeError('Este entrenamiento requiere CUDA.')
dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=dtype, bnb_4bit_use_double_quant=True)
tokenizer = AutoTokenizer.from_pretrained(MODELO)
model = AutoModelForCausalLM.from_pretrained(MODELO, quantization_config=quant, device_map={'': 0}, torch_dtype=dtype)
model.config.use_cache = False
model = prepare_model_for_kbit_training(model)
dataset = load_dataset('json', data_files=DATOS, split='train')

# Qwen3: desactivamos el modo thinking para un ajuste instructivo convencional.
def formatear(ejemplo):
    return tokenizer.apply_chat_template(ejemplo['messages'], tokenize=False, add_generation_prompt=False, enable_thinking=False)

dataset = dataset.map(lambda x: {'text': formatear(x)}, remove_columns=dataset.column_names)

lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias='none', task_type='CAUSAL_LM', target_modules='all-linear')
args = TrainingArguments(output_dir=SALIDA, per_device_train_batch_size=1, gradient_accumulation_steps=8, num_train_epochs=3, learning_rate=2e-4, logging_steps=5, save_strategy='epoch', gradient_checkpointing=True, bf16=(dtype == torch.bfloat16), fp16=(dtype == torch.float16), optim='paged_adamw_8bit', report_to='none', remove_unused_columns=False)
trainer = SFTTrainer(model=model, train_dataset=dataset, args=args, peft_config=lora, processing_class=tokenizer)
trainer.train()
trainer.save_model(SALIDA)
tokenizer.save_pretrained(SALIDA)
print(f'Adaptador guardado en {SALIDA}')