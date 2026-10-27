import argparse
import json
import re
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import requests

OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'granite4.1:8b'
EXTENSIONES = {'.txt', '.md'}


def limpiar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()


def crear_chunks(texto, tamano=1500, overlap=200):
    if tamano <= 0 or overlap < 0 or overlap >= tamano:
        raise ValueError('El overlap debe ser >= 0 y menor que el tamaño positivo')
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fin = min(inicio + tamano, len(texto))
        if fin < len(texto):
            segmento = texto[inicio:fin]
            corte = max(segmento.rfind('. '), segmento.rfind('? '), segmento.rfind('! '))
            if corte > tamano // 2:
                fin = inicio + corte + 1
        chunk = texto[inicio:fin].strip()
        if chunk:
            chunks.append(chunk)
        if fin >= len(texto):
            break
        inicio = max(inicio + 1, fin - overlap)
    return chunks


def generar_pareja(session, parrafo, modelo):
    prompt = f'''You are creating high-quality training data for a semantic embedding model.
Read this source paragraph:
<source>\n{parrafo}\n</source>
Generate exactly TWO different sentences in Spanish.
Both sentences must express the same meaning, using different vocabulary and grammatical structures.
Preserve important facts; both must be independently understandable.
Do not invent information or introduce contradictions. Return ONLY valid JSON.
{{"sentence1": "...", "sentence2": "..."}}'''
    respuesta = session.post(OLLAMA_URL, json={
        'model': modelo, 'prompt': prompt, 'stream': False, 'format': 'json',
        'options': {'temperature': 0.5, 'num_ctx': 8192}
    }, timeout=300)
    respuesta.raise_for_status()
    datos = json.loads(respuesta.json()['response'])
    a, b = datos.get('sentence1', '').strip(), datos.get('sentence2', '').strip()
    if not a or not b or a == b:
        raise ValueError('Pareja vacía o frases idénticas')
    return {'sentence1': a, 'sentence2': b}


def duracion(segundos):
    return str(timedelta(seconds=int(max(0, segundos))))


def main():
    parser = argparse.ArgumentParser(description='Generar parejas semánticas desde una carpeta')
    parser.add_argument('carpeta', type=Path)
    parser.add_argument('--output', type=Path, default=Path('training_pairs.jsonl'))
    parser.add_argument('--chunk-size', type=int, default=1500)
    parser.add_argument('--overlap', type=int, default=200)
    parser.add_argument('--model', default=MODEL)
    parser.add_argument('--no-recursive', action='store_true')
    args = parser.parse_args()
    if not args.carpeta.is_dir():
        parser.error('La carpeta no existe')
    if args.chunk_size <= 0 or not 0 <= args.overlap < args.chunk_size:
        parser.error('chunk-size debe ser positivo y overlap menor que chunk-size')

    raiz = args.carpeta.resolve()
    salida = args.output.resolve()
    archivos = sorted(p for p in (raiz.iterdir() if args.no_recursive else raiz.rglob('*'))
                      if p.is_file() and p.resolve() != salida)
    extensiones = Counter((p.suffix.lower() or '[sin extensión]') for p in archivos)
    trabajos = []
    total_caracteres = 0
    print('\n=== INVENTARIO DE ARCHIVOS ===')
    print(f'Carpeta: {raiz}\nArchivos encontrados: {len(archivos)}')
    for ext, cantidad in sorted(extensiones.items()):
        print(f'  {ext}: {cantidad} archivos')
    print('\n=== ARCHIVOS DE TEXTO ===')
    for ruta in archivos:
        if ruta.suffix.lower() not in EXTENSIONES:
            continue
        try:
            texto = limpiar_texto(ruta.read_text(encoding='utf-8-sig'))
        except (OSError, UnicodeError) as exc:
            print(f'OMITIDO {ruta}: {exc}')
            continue
        chunks = crear_chunks(texto, args.chunk_size, args.overlap)
        total_caracteres += len(texto)
        trabajos.append((ruta, chunks))
        print(f'{ruta.relative_to(raiz)} | {len(texto):,} caracteres | {len(chunks)} chunks')

    total = sum(len(chunks) for _, chunks in trabajos)
    print(f'\nTOTAL: {len(trabajos)} archivos de texto, {total_caracteres:,} caracteres, {total:,} chunks')
    if not total:
        print('No hay texto que procesar.')
        return

    # La salida JSONL es la fuente de verdad para la reanudación.
    # Cada chunk se identifica por ruta relativa, índice y hash de su contenido.
    import hashlib
    completados = set()
    if salida.exists():
        with salida.open('r', encoding='utf-8') as f:
            for linea in f:
                try:
                    r = json.loads(linea)
                    if all(k in r for k in ('source_file', 'chunk_id', 'chunk_hash')):
                        completados.add((r['source_file'], r['chunk_id'], r['chunk_hash']))
                except (ValueError, TypeError):
                    continue
    pendientes = []
    for ruta, chunks in trabajos:
        relativo = ruta.relative_to(raiz).as_posix()
        for i, chunk in enumerate(chunks):
            h = hashlib.sha256(chunk.encode('utf-8')).hexdigest()
            if (relativo, i, h) not in completados:
                pendientes.append((relativo, i, chunk, h))
    print(f'Ya completados: {total - len(pendientes)} | Pendientes: {len(pendientes)}')
    if not pendientes:
        print('Proceso completado.')
        return

    inicio = time.monotonic()
    hechos = 0
    session = requests.Session()
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open('a', encoding='utf-8') as f:
        for relativo, indice, chunk, h in pendientes:
            try:
                pareja = generar_pareja(session, chunk, args.model)
                registro = {'source_file': relativo, 'chunk_id': indice, 'chunk_hash': h, **pareja}
                f.write(json.dumps(registro, ensure_ascii=False) + '\n')
                f.flush()
            except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
                print(f'\nERROR en {relativo} chunk {indice}: {exc}\nReejecuta el comando para continuar.')
                break
            hechos += 1
            transcurrido = time.monotonic() - inicio
            promedio = transcurrido / hechos
            restante = (len(pendientes) - hechos) * promedio
            porcentaje = 100 * (total - len(pendientes) + hechos) / total
            fin = datetime.now() + timedelta(seconds=restante)
            print(f'[{total - len(pendientes) + hechos}/{total}] {porcentaje:.1f}% | '
                  f'{relativo} #{indice} | {promedio:.1f}s/chunk | '
                  f'Transcurrido {duracion(transcurrido)} | '
                  f'Restante {duracion(restante)} | Fin aprox. {fin:%Y-%m-%d %H:%M:%S}', flush=True)
        else:
            print(f'\nCOMPLETADO: {salida}')


if __name__ == '__main__':
    main()