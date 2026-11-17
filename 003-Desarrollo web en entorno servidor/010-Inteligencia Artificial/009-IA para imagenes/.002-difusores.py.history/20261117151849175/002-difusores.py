
import torch
from diffusers import StableDiffusionPipeline

modelo = "stable-diffusion-v1-5/stable-diffusion-v1-5"

print("Loading model...")

pipe = StableDiffusionPipeline.from_pretrained(
    modelo,
    torch_dtype=torch.float16,
    use_safetensors=True
)

pipe = pipe.to("cuda")

prompt = "A futuristic city at sunset, cinematic lighting, photorealistic, highly detailed"

print("Generating image...")

imagen = pipe(
    prompt,
    width=512,
    height=512,
    num_inference_steps=30,
    guidance_scale=7.5
).images[0]

imagen.save("resultado.png")

print("Image saved: resultado.png")
