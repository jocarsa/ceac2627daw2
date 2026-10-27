#!/usr/bin/env python3
"""Genera un MP4 de 10 segundos por película del JSON."""
import argparse
import json
import random
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ANCHO, ALTO = 1280, 720


def fuente(tamano):
    opciones = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
    ]
    for ruta in opciones:
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tamano)
    raise RuntimeError('Instala una fuente TrueType: sudo apt install fonts-dejavu-core')


def partir_titulo(texto, draw, font, ancho_maximo):
    lineas, actual = [], ''
    for palabra in texto.split():
        prueba = (actual + ' ' + palabra).strip()
        if actual and draw.textbbox((0, 0), prueba, font=font)[2] > ancho_maximo:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return '\n'.join(lineas)


def crear_fotograma(titulo, destino, rng):
    fondo = tuple(rng.randint(30, 185) for _ in range(3))
    imagen = Image.new('RGB', (ANCHO, ALTO), fondo)
    dibujo = ImageDraw.Draw(imagen)
    for tamano in range(86, 27, -2):
        tipografia = fuente(tamano)
        texto = partir_titulo(titulo, dibujo, tipografia, 1080)
        caja = dibujo.multiline_textbbox((0, 0), texto, font=tipografia, spacing=18, align='center', stroke_width=2)
        if caja[2] - caja[0] <= 1100 and caja[3] - caja[1] <= 520:
            break
    x = (ANCHO - (caja[2] - caja[0])) / 2 - caja[0]
    y = (ALTO - (caja[3] - caja[1])) / 2 - caja[1]
    dibujo.multiline_text((x, y), texto, font=tipografia, fill='white',
                          spacing=18, align='center', stroke_width=2,
                          stroke_fill=(0, 0, 0))
    imagen.save(destino, 'PNG')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json', nargs='?', default='titulos.json')
    parser.add_argument('--salida', default='videos')
    parser.add_argument('--limite', type=int, default=500)
    parser.add_argument('--sobrescribir', action='store_true')
    args = parser.parse_args()
    if not shutil.which('ffmpeg'):
        raise SystemExit('Falta FFmpeg: sudo apt install ffmpeg')
    with open(args.json, encoding='utf-8') as archivo:
        datos = json.load(archivo)
    peliculas = datos['peliculas'] if isinstance(datos, dict) else datos
    peliculas = peliculas[:args.limite]
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    rng = random.Random()
    total = len(peliculas)
    for indice, pelicula in enumerate(peliculas, 1):
        identificador = int(pelicula.get('id', indice))
        titulo = str(pelicula['titulo'])
        mp4 = salida / f'{identificador:03d}.mp4'
        if mp4.exists() and not args.sobrescribir:
            print(f'[{indice}/{total}] Ya existe: {mp4}', flush=True)
            continue
        png = salida / f'.temporal_{identificador:03d}.png'
        try:
            crear_fotograma(titulo, png, rng)
            comando = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                       '-loop', '1', '-framerate', '25', '-i', str(png),
                       '-t', '10', '-c:v', 'libx264', '-preset', 'ultrafast',
                       '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
                       '-r', '25', '-movflags', '+faststart', str(mp4)]
            subprocess.run(comando, check=True)
            print(f'[{indice}/{total}] Generado: {mp4} — {titulo}', flush=True)
        finally:
            png.unlink(missing_ok=True)
    print(f'Finalizado. Vídeos disponibles en: {salida.resolve()}')


if __name__ == '__main__':
    main()
