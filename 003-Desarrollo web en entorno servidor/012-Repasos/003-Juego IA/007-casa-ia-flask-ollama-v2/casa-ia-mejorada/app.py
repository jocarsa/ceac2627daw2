from flask import Flask, jsonify, request, send_from_directory
import os, requests, math, json, threading, time

ROOT=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__,static_folder=None)
MODEL=os.environ.get('OLLAMA_MODEL','qwen2.5:3b')
OLLAMA=os.environ.get('OLLAMA_URL','http://127.0.0.1:11434/api/chat')
COOLDOWN=float(os.environ.get('AI_COOLDOWN','12'))
ROOMS={'salon':'aburrimiento','cocina':'sed','dormitorio':'cansancio','bano':'pipi'}
SCHEMA={'type':'object','properties':{'destino':{'type':'string','enum':list(ROOMS)},'accion':{'type':'string'},'motivo':{'type':'string'}},'required':['destino','accion','motivo']}
LOCK=threading.Lock()
CACHE={'at':0,'decision':None}

@app.get('/')
def index(): return send_from_directory(ROOT,'index.html')

@app.get('/sprite.png')
def sprite():
    path=os.path.join(ROOT,'sprite.png')
    if not os.path.isfile(path): return ('',404)
    return send_from_directory(ROOT,'sprite.png')

@app.get('/api/estado')
def estado():
    try:
        r=requests.get(OLLAMA.replace('/api/chat','/api/tags'),timeout=3)
        r.raise_for_status()
        names=[m.get('name','') for m in r.json().get('models',[])]
        return jsonify(ok=True,modelo=MODEL,disponible=MODEL in names,modelos=names,ocupado=LOCK.locked())
    except requests.RequestException as e:
        return jsonify(ok=False,modelo=MODEL,error=str(e)),503

@app.post('/api/decidir')
def decidir():
    body=request.get_json(silent=True) or {}
    try:
        needs={k:max(0,min(100,float(body.get(k,0)))) for k in ('sed','pipi','cansancio','aburrimiento')}
        if not all(math.isfinite(v) for v in needs.values()): raise ValueError('Valores no finitos')
    except (ValueError,TypeError): return jsonify(ok=False,error='Necesidades inválidas'),400
    if not LOCK.acquire(blocking=False):
        return jsonify(ok=False,ocupado=True,error='Ollama está procesando otra decisión'),429
    try:
        now=time.monotonic()
        if CACHE['decision'] is not None and now-CACHE['at']<COOLDOWN:
            return jsonify(ok=True,cache=True,**CACHE['decision'])
        actual=str(body.get('habitacion',''))[:30]
        previo=str(body.get('destino_actual',''))[:30]
        prompt=(f'Personaje de simulador. Necesidades de 0 (bien) a 100 (urgente): {needs}. '
                f'Habitación actual: {actual}; destino anterior: {previo}. '
                'Habitaciones: salon reduce aburrimiento, cocina reduce sed, dormitorio reduce cansancio, bano reduce pipi. '
                'Elige la necesidad más urgente; evita cambiar de destino sin motivo. '
                'Devuelve JSON con destino válido, accion y motivo breve, natural y en primera persona, en español (máximo 12 palabras).')
        try:
            r=requests.post(OLLAMA,json={'model':MODEL,'messages':[{'role':'system','content':'Eres un personaje de videojuego. Responde únicamente JSON válido.'},{'role':'user','content':prompt}],'format':SCHEMA,'stream':False,'options':{'temperature':0.1,'num_predict':100},'keep_alive':'20m'},timeout=(5,120))
            r.raise_for_status()
            decision=json.loads(r.json()['message']['content'])
            if decision.get('destino') not in ROOMS: raise ValueError('Destino desconocido')
            clean={'modelo':MODEL,'destino':decision['destino'],'accion':str(decision.get('accion',''))[:90],'motivo':str(decision.get('motivo',''))[:180]}
            CACHE.update(at=time.monotonic(),decision=clean)
            return jsonify(ok=True,cache=False,**clean)
        except requests.RequestException as e:
            app.logger.exception('Fallo Ollama')
            return jsonify(ok=False,error=f'Error Ollama: {e}'),503
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:
            app.logger.exception('Respuesta inválida de Ollama')
            return jsonify(ok=False,error=f'Respuesta inválida: {e}'),503
    finally:
        LOCK.release()

if __name__=='__main__':
    print(f'Modelo: {MODEL} | Ollama: {OLLAMA} | http://127.0.0.1:5000')
    app.run(host='127.0.0.1',port=5000,threaded=True)
