import os, json, threading, time
from flask import Flask, jsonify, render_template
import clasificador_original as motor

app = Flask(__name__)
lock = threading.RLock()
state = {'running': False, 'stop': False, 'current': '', 'done': 0, 'total': 0, 'errors': 0, 'message': 'Preparado'}

def records():
    data = {}
    if os.path.isfile(motor.ARCHIVO_RESULTADOS):
        with open(motor.ARCHIVO_RESULTADOS, encoding='utf-8') as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get('ruta'): data[r['ruta']] = r
                except (ValueError, TypeError): pass
    return data

def worker():
    try:
        paths = motor.buscar_pdfs()
        with lock: state.update(total=len(paths), done=0, errors=0, message='Clasificando documentos')
        cached = records()
        for path in paths:
            with lock:
                if state['stop']: break
                state['current'] = os.path.basename(path)
            try:
                sig = motor.firma_archivo(path)
                if path not in cached or cached[path].get('firma') != sig:
                    start = time.time()
                    info = motor.extraer_texto(path)
                    if info['texto']:
                        result = motor.analizar_documento(info['texto'], os.path.basename(path))
                    else:
                        result = dict(resumen='No se ha podido extraer texto del documento.', categoria='Archivo y pendientes', subcategoria='Documentos sin texto', tokens_entrada=0, tokens_salida=0)
                    record = dict(ruta=path, archivo=os.path.basename(path), firma=sig, fecha_analisis=time.strftime('%Y-%m-%dT%H:%M:%S'), modelo=motor.MODELO, caracteres_analizados=len(info['texto']), paginas_totales=info['paginas_totales'], resumen=result['resumen'], categoria=result['categoria'], subcategoria=result['subcategoria'], duracion_segundos=round(time.time()-start, 2), tokens_entrada=result['tokens_entrada'], tokens_salida=result['tokens_salida'])
                    motor.guardar_jsonl(motor.ARCHIVO_RESULTADOS, record)
                    cached[path] = record
            except Exception as exc:
                motor.guardar_jsonl(motor.ARCHIVO_ERRORES, {'ruta':path,'fecha':time.strftime('%Y-%m-%dT%H:%M:%S'),'error':str(exc)})
                with lock: state['errors'] += 1
            finally:
                with lock: state['done'] += 1
        with lock: state['message'] = 'Detenido' if state['stop'] else 'Finalizado'
    except Exception as exc:
        with lock: state['message'] = f'Error: {exc}'
    finally:
        with lock: state.update(running=False, current='')

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/status')
def status():
    rs = list(records().values())
    rs.sort(key=lambda x:x.get('fecha_analisis',''), reverse=True)
    tree = {}
    for r in rs:
        tree.setdefault(r.get('categoria','Archivo y pendientes'), {}).setdefault(r.get('subcategoria','Sin clasificar'), []).append({'archivo':r.get('archivo',''), 'ruta':r['ruta'], 'resumen':r.get('resumen','')})
    with lock: s = state.copy()
    s.update(records=rs, tree=tree, classified=len(rs), percentage=round(100*s['done']/s['total'],1) if s['total'] else 0, simulation=True)
    return jsonify(s)

@app.post('/api/start')
def start():
    with lock:
        if state['running']: return jsonify(ok=False, message='Ya está ejecutándose'), 409
        state.update(running=True, stop=False, current='', done=0, errors=0, message='Iniciando')
    threading.Thread(target=worker, daemon=True).start()
    return jsonify(ok=True)

@app.post('/api/stop')
def stop():
    with lock: state['stop'] = True; state['message'] = 'Deteniendo tras el documento actual'
    return jsonify(ok=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
