import ast
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import requests

# CONFIGURACIÓN ####################################################
RUTA = os.getenv('JOCARSA_DAW_URL', 'https://ages-friend-follow-jeremy.trycloudflare.com/daw/')
TOKEN = os.getenv('JOCARSA_DAW_API_TOKEN', 'jocarsa_phi4_2026_ClaveSegura_8f3a91b7')
MODELO_GENERADOR = os.getenv('MODELO_GENERADOR', 'gemma4:e4b')
MODELO_EVALUADOR = os.getenv('MODELO_EVALUADOR', 'gpt-oss:20b')
DIRECTORIO = Path(__file__).resolve().parent
CARPETA = DIRECTORIO / 'objetivo'
DIAGNOSTICOS = DIRECTORIO / 'diagnosticos_crud'
TIMEOUT = 650
MAX_ARCHIVOS = 30
MAX_BYTES_ARCHIVO = 100_000
MAX_CARACTERES_EVALUACION = 100_000
INTENTOS_JSON = 2
INTENTOS_ARCHIVO = 3
ESPERA_REINTENTO = 3
ARCHIVOS_INTERNOS = {'objetivo.txt', 'informe_contenido.md', 'informe_evaluacion.md'}
SESION = requests.Session()


def registrar(nombre, contenido):
    DIAGNOSTICOS.mkdir(parents=True, exist_ok=True)
    ruta = DIAGNOSTICOS / nombre
    ruta.write_text(str(contenido), encoding='utf-8', errors='replace')
    return ruta


def obtener_texto_api(objeto):
    if isinstance(objeto, str):
        return objeto
    if isinstance(objeto, list):
        textos = [obtener_texto_api(x) for x in objeto]
        return '\n'.join(x for x in textos if x)
    if not isinstance(objeto, dict):
        return ''
    if objeto.get('error'):
        raise ValueError(f"Error de API: {objeto['error']}")
    if isinstance(objeto.get('archivos'), list):
        return json.dumps(objeto, ensure_ascii=False)
    for clave in ('response', 'respuesta', 'resultado', 'texto', 'content', 'mensaje', 'output', 'message'):
        if clave in objeto:
            texto = obtener_texto_api(objeto[clave])
            if texto.strip():
                return texto
    for clave in ('choices', 'data'):
        if clave in objeto:
            texto = obtener_texto_api(objeto[clave])
            if texto.strip():
                return texto
    return ''


def preguntar_ia(modelo, pregunta, etiqueta, json_requerido=False):
    if json_requerido:
        pregunta += '\n\nDevuelve SOLO JSON válido. Sin fences ni texto adicional.'
    datos = {'token': TOKEN, 'modelo': modelo, 'mensaje': pregunta, 'stream': False}
    print(f'\nConsultando API externa: {modelo} [{etiqueta}]', flush=True)
    ultimo_error = None
    for intento in range(1, 4):
        try:
            respuesta = SESION.post(RUTA, json=datos, timeout=(20, TIMEOUT))
            registrar(f'{etiqueta}_http.txt', f'HTTP {respuesta.status_code}\nContent-Type: {respuesta.headers.get("Content-Type")}\n\n{respuesta.text}')
            respuesta.raise_for_status()
            if not respuesta.content.strip():
                raise ValueError('Respuesta HTTP vacía')
            try:
                cuerpo = respuesta.json()
            except ValueError as error:
                raise ValueError(f'La API no devolvió JSON HTTP: {respuesta.text[:350]!r}') from error
            texto = obtener_texto_api(cuerpo)
            if not texto.strip():
                raise ValueError(f'La API no contiene texto generado. Claves: {list(cuerpo) if isinstance(cuerpo, dict) else type(cuerpo).__name__}')
            registrar(f'{etiqueta}_modelo.txt', texto)
            return texto
        except (requests.RequestException, ValueError) as error:
            ultimo_error = error
            print(f'  Intento HTTP {intento}/3: {error}')
            if intento < 3:
                time.sleep(ESPERA_REINTENTO * intento)
    raise RuntimeError(f'Fallo consultando API [{etiqueta}]: {ultimo_error}')


def candidatos_json(texto):
    texto = texto.lstrip('\ufeff').strip()
    yield texto
    for coincidencia in re.finditer(r'```(?:json)?\s*(.*?)```', texto, re.I | re.S):
        yield coincidencia.group(1).strip()
    decodificador = json.JSONDecoder(strict=False)
    for indice, caracter in enumerate(texto):
        if caracter != '{':
            continue
        try:
            objeto, _ = decodificador.raw_decode(texto[indice:])
            if isinstance(objeto, dict):
                yield json.dumps(objeto, ensure_ascii=False)
                return
        except json.JSONDecodeError:
            continue
    inicio = texto.find('{')
    fin = texto.rfind('}')
    if inicio >= 0 and fin > inicio:
        yield texto[inicio:fin + 1]


def extraer_json(texto):
    errores = []
    for candidato in candidatos_json(texto):
        try:
            return json.loads(candidato, strict=False)
        except json.JSONDecodeError as error:
            errores.append(str(error))
        # Reparaciones conservadoras: comas finales y BOM. No alterar cadenas de código.
        reparado = re.sub(r',\s*([}\]])', r'\1', candidato)
        try:
            return json.loads(reparado, strict=False)
        except json.JSONDecodeError:
            pass
        # json_repair es opcional y se usa solo si está instalado.
        try:
            from json_repair import repair_json
            objeto = repair_json(candidato, return_objects=True)
            if isinstance(objeto, dict):
                return objeto
        except (ImportError, ValueError, TypeError, Exception):
            pass
    raise ValueError('JSON generado inválido: ' + '; '.join(errores[:2]))


def validar_ruta(nombre):
    if not isinstance(nombre, str) or not nombre or '\\' in nombre or '\x00' in nombre:
        raise ValueError(f'Ruta inválida: {nombre!r}')
    ruta = Path(nombre)
    if ruta.is_absolute() or any(parte in ('', '.', '..') for parte in nombre.split('/')):
        raise ValueError(f'Ruta insegura: {nombre!r}')
    if ruta.name in ARCHIVOS_INTERNOS or ruta.parts[0].startswith('.'):
        raise ValueError(f'Ruta reservada: {nombre!r}')
    if ruta.suffix.lower() not in ('.php', '.css', '.js', '.html', '.json', '.md', '.txt', '.sql', '.svg'):
        raise ValueError(f'Extensión no permitida: {nombre!r}')
    return ruta


def validar_proyecto(proyecto):
    if not isinstance(proyecto, dict):
        raise ValueError('La raíz del JSON debe ser un objeto')
    archivos = proyecto.get('archivos')
    if not isinstance(archivos, list) or not 1 <= len(archivos) <= MAX_ARCHIVOS:
        raise ValueError('Lista archivos ausente o fuera de límites')
    vistos = set()
    for archivo in archivos:
        if not isinstance(archivo, dict):
            raise ValueError('Cada archivo debe ser un objeto')
        ruta = validar_ruta(archivo.get('ruta'))
        contenido = archivo.get('contenido')
        if not isinstance(contenido, str) or not contenido.strip():
            raise ValueError(f'Contenido vacío o inválido: {ruta}')
        if len(contenido.encode('utf-8')) > MAX_BYTES_ARCHIVO:
            raise ValueError(f'Archivo demasiado grande: {ruta}')
        if str(ruta) in vistos:
            raise ValueError(f'Archivo duplicado: {ruta}')
        vistos.add(str(ruta))
    if 'index.php' not in vistos:
        raise ValueError('Falta index.php')
    return proyecto


def limpiar_codigo(texto, nombre):
    texto = texto.strip().lstrip('\ufeff')
    patron = re.compile(r'^```[^\n]*\n(.*?)\n```\s*$', re.S)
    encontrado = patron.match(texto)
    if encontrado:
        texto = encontrado.group(1)
    if nombre.endswith('.php'):
        posicion = texto.find('<?php')
        if posicion > 0:
            texto = texto[posicion:]
    return texto.rstrip() + '\n'


def prompt_base(objetivo):
    return f'''Eres desarrollador senior PHP 8 y SQLite. Crea un CRUD completo para: {objetivo}
Requisitos: alta, listado, edición, borrado, búsqueda, validación servidor, PDO con parámetros, escape HTML, interfaz responsive, SQLite auto-inicializado, sin frameworks ni dependencias externas. No uses TODO ni pseudocódigo.
Usa exactamente index.php, estilo.css y app.js; enlázalos correctamente. index.php contiene la lógica PHP y la inicialización SQLite. El formulario POST distingue acciones crear, actualizar y borrar. Redirige tras POST. Escapa las salidas HTML. Usa rutas relativas.'''


def generar_por_archivos(objetivo):
    print('\nActivando recuperación: generación independiente por archivo.')
    especificaciones = {
        'index.php': 'Genera PHP 8 completo con HTML, PDO SQLite, CRUD y enlaces a estilo.css y app.js. Debe ser autosuficiente.',
        'estilo.css': 'Genera CSS completo y responsive para la estructura HTML del index.php suministrado.',
        'app.js': 'Genera JavaScript progresivo para la estructura HTML del index.php suministrado, sin dependencias.'
    }
    resultado = []
    contexto = ''
    for nombre, especificacion in especificaciones.items():
        ultimo = None
        for intento in range(1, INTENTOS_ARCHIVO + 1):
            pregunta = prompt_base(objetivo) + f'\n\nARCHIVO ACTUAL: {nombre}\n{especificacion}\nDevuelve ÚNICAMENTE el contenido del archivo, sin JSON ni Markdown.\n' + contexto[:12000]
            try:
                contenido = limpiar_codigo(preguntar_ia(MODELO_GENERADOR, pregunta, f'archivo_{nombre.replace(".", "_")}_{intento}'), nombre)
                if not contenido.strip() or len(contenido.encode('utf-8')) > MAX_BYTES_ARCHIVO:
                    raise ValueError('Contenido vacío o demasiado grande')
                if nombre == 'index.php' and ('<?php' not in contenido or 'PDO' not in contenido):
                    raise ValueError('El PHP no parece contener el CRUD solicitado')
                if nombre == 'index.php' and shutil.which('php'):
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.php', encoding='utf-8', delete=False) as temporal:
                        temporal.write(contenido)
                        temporal_nombre = temporal.name
                    try:
                        prueba = subprocess.run(['php', '-l', temporal_nombre], capture_output=True, text=True, timeout=15)
                        if prueba.returncode:
                            raise ValueError('PHP inválido: ' + (prueba.stderr or prueba.stdout)[:300])
                    finally:
                        Path(temporal_nombre).unlink(missing_ok=True)
                resultado.append({'ruta': nombre, 'contenido': contenido})
                if nombre == 'index.php':
                    contexto = '\nReferencia de estructura HTML/PHP ya generada:\n' + contenido[:12000]
                print(f'  Validado: {nombre}')
                break
            except (ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
                ultimo = error
                print(f'  {nombre} intento {intento}: {error}')
        else:
            raise RuntimeError(f'No se pudo generar {nombre}: {ultimo}')
    return validar_proyecto({'nombre': objetivo, 'descripcion': objetivo, 'archivos': resultado})


def agente_generador(objetivo):
    print('\n========== AGENTE 1: GENERADOR ==========')
    base = prompt_base(objetivo)
    error_previo = ''
    for intento in range(1, INTENTOS_JSON + 1):
        prompt = base + '''\nEntrega SOLO un objeto JSON con claves nombre, descripcion y archivos. archivos es una lista de objetos {"ruta":"index.php","contenido":"..."}, {"ruta":"estilo.css","contenido":"..."}, {"ruta":"app.js","contenido":"..."}. Escapa correctamente saltos de línea, comillas y barras invertidas dentro de cadenas JSON. No incluyas texto fuera del JSON.'''
        if error_previo:
            prompt += '\nTu respuesta anterior falló por: ' + error_previo[:500] + '. Regenera JSON completo y válido.'
        try:
            texto = preguntar_ia(MODELO_GENERADOR, prompt, f'generador_json_{intento}', json_requerido=True)
            proyecto = validar_proyecto(extraer_json(texto))
            print('  JSON validado correctamente.')
            return proyecto
        except (ValueError, RuntimeError) as error:
            error_previo = str(error)
            print(f'  JSON intento {intento}/{INTENTOS_JSON} fallido: {error}')
    return generar_por_archivos(objetivo)


def guardar_proyecto(proyecto, objetivo):
    validar_proyecto(proyecto)
    # Preparar todo antes de tocar el proyecto anterior.
    CARPETA.parent.mkdir(parents=True, exist_ok=True)
    temporal = Path(tempfile.mkdtemp(prefix='crud_nuevo_', dir=CARPETA.parent))
    try:
        for archivo in proyecto['archivos']:
            ruta = validar_ruta(archivo['ruta'])
            destino = temporal / ruta
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(archivo['contenido'], encoding='utf-8')
        (temporal / 'objetivo.txt').write_text(objetivo, encoding='utf-8')
        # No seguir enlaces simbólicos ni reutilizar archivos del proyecto antiguo.
        copia = CARPETA.with_name(CARPETA.name + '_anterior')
        if copia.exists():
            if copia.is_symlink():
                copia.unlink()
            else:
                shutil.rmtree(copia)
        if CARPETA.exists() or CARPETA.is_symlink():
            CARPETA.rename(copia)
        try:
            temporal.rename(CARPETA)
        except OSError:
            if copia.exists():
                copia.rename(CARPETA)
            raise
        print(f'  Proyecto guardado en: {CARPETA}')
        if copia.exists():
            print(f'  Copia anterior: {copia}')
    finally:
        if temporal.exists():
            shutil.rmtree(temporal)
    return obtener_archivos_proyecto()


def obtener_archivos_proyecto():
    if not CARPETA.is_dir():
        return []
    return [p for p in sorted(CARPETA.rglob('*')) if p.is_file() and not p.is_symlink() and p.name not in ARCHIVOS_INTERNOS]


def comprobar_sintaxis(archivo):
    extension = archivo.suffix.lower()
    try:
        if extension == '.py':
            ast.parse(archivo.read_text(encoding='utf-8'))
            return 'Python: sintaxis correcta'
        if extension == '.json':
            json.loads(archivo.read_text(encoding='utf-8'))
            return 'JSON: válido'
        if extension == '.php':
            if not shutil.which('php'):
                return 'PHP CLI no instalado: sin comprobar'
            resultado = subprocess.run(['php', '-l', str(archivo)], capture_output=True, text=True, timeout=15)
            return ('OK: ' if resultado.returncode == 0 else 'ERROR: ') + (resultado.stdout + resultado.stderr).strip()
    except (SyntaxError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        return f'ERROR: {error}'
    return 'Sin comprobación automática'


def generar_informe_carpeta(archivos):
    partes = ['# INVENTARIO DEL PROYECTO\n']
    total_lineas = total_bytes = 0
    for archivo in archivos:
        contenido = archivo.read_text(encoding='utf-8', errors='replace')
        lineas, tamano = len(contenido.splitlines()), archivo.stat().st_size
        total_lineas += lineas
        total_bytes += tamano
        partes.append(f'- {archivo.relative_to(CARPETA)} | {lineas} líneas | {tamano} bytes')
    partes.extend(['\n# ESTADÍSTICAS GENERALES', f'- Número de archivos: {len(archivos)}', f'- Total de líneas: {total_lineas}', f'- Tamaño total: {total_bytes} bytes', '\n# CONTENIDO Y SINTAXIS'])
    for archivo in archivos:
        contenido = archivo.read_text(encoding='utf-8', errors='replace')
        partes.extend([f'\n## ARCHIVO: {archivo.relative_to(CARPETA)}', f'Comprobación: {comprobar_sintaxis(archivo)}', '\nCONTENIDO:\n', contenido])
    informe = '\n'.join(partes)
    if len(informe) > MAX_CARACTERES_EVALUACION:
        informe = informe[:MAX_CARACTERES_EVALUACION] + '\n\n[INFORME TRUNCADO: el evaluador no ha recibido el código completo]'
    return informe


def agente_evaluador(objetivo, archivos):
    print('\n========== AGENTE 2: EVALUADOR ==========')
    informe = generar_informe_carpeta(archivos)
    (CARPETA / 'informe_contenido.md').write_text(informe, encoding='utf-8')
    prompt = f'''Eres auditor senior de software. Evalúa estrictamente un CRUD PHP/SQLite, sin modificar archivos ni inventar pruebas.
OBJETIVO: {objetivo}
CÓDIGO Y COMPROBACIONES:\n{informe}
Diferencia funcionalidad observada, comprobada y no verificada. Analiza CREATE, READ, UPDATE, DELETE, validación, PDO, XSS, estructura, interfaz, errores y coherencia. No afirmes que se ha ejecutado la aplicación si solo se comprobó sintaxis.
Devuelve SOLO Markdown con estos apartados:
# INFORME DE EVALUACIÓN
## 1. Resumen ejecutivo
## 2. Cumplimiento del objetivo
## 3. Evaluación del CRUD
## 4. Calidad del código
## 5. Seguridad
## 6. Diseño e interfaz
## 7. Errores detectados
## 8. Mejoras recomendadas
## 9. Puntuación final (0-100)
## 10. Veredicto: APROBADO o SUSPENDIDO'''
    evaluacion = preguntar_ia(MODELO_EVALUADOR, prompt, 'evaluacion')
    if len(evaluacion.strip()) < 100:
        raise ValueError('Informe de evaluación sospechosamente corto')
    (CARPETA / 'informe_evaluacion.md').write_text(evaluacion, encoding='utf-8')
    return evaluacion


def main():
    print('=' * 60)
    print('JOCARSA | GENERADOR Y EVALUADOR DE CRUD ROBUSTO')
    print('=' * 60)
    print('\n1.- Generar un nuevo CRUD y evaluarlo')
    print('2.- Evaluar el CRUD existente')
    opcion = input('\nOpción [1/2]: ').strip()
    if opcion == '1':
        objetivo = input('\n¿Qué aplicación CRUD quieres crear?\n> ').strip()
        if not objetivo:
            print('No has indicado ningún objetivo.')
            return
        proyecto = agente_generador(objetivo)
        archivos = guardar_proyecto(proyecto, objetivo)
        print('\nAplicación generada:', proyecto.get('nombre', 'Sin nombre'))
    elif opcion == '2':
        ruta_objetivo = CARPETA / 'objetivo.txt'
        if not ruta_objetivo.is_file():
            print('No existe objetivo.txt')
            return
        objetivo = ruta_objetivo.read_text(encoding='utf-8')
        archivos = obtener_archivos_proyecto()
        if not archivos:
            print('No hay archivos para evaluar')
            return
        print('\nProyecto existente encontrado:')
        for archivo in archivos:
            print(' ', archivo.relative_to(CARPETA))
    else:
        print('Opción no válida')
        return
    evaluacion = agente_evaluador(objetivo, archivos)
    print('\n========== RESULTADO ==========\n')
    print(evaluacion)
    print('\nPROCESO FINALIZADO')
    print('Carpeta:', CARPETA)
    print('Diagnósticos:', DIAGNOSTICOS)


if __name__ == '__main__':
    try:
        main()
    except (requests.RequestException, RuntimeError, ValueError, KeyError, TypeError, OSError) as error:
        print(f'\nERROR: {error}')
        raise SystemExit(1)
