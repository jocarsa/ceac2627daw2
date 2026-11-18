from flask import Flask, jsonify, request, send_from_directory
import os, requests, math

ROOT=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__,static_folder=None)
MODEL=os.environ.get('OLLAMA_MODEL','qwen2.5:3b')
OLLAMA=os.environ.get('OLLAMA_URL','http://127.0.0.1:11434/api/chat')
ROOMS={'salon':'aburrimiento','cocina':'sed','dormitorio':'cansancio','bano':'pipi'}
SCHEMA={'type':'object','properties':{'destino':{'type':'string','enum':list(ROOMS)},'accion':{'type':'string'},'motivo':{'type':'string'}},'required':['destino','accion','motivo']}

@app.get('/')
def index(): return send_from_directory(ROOT,'index.html')

@app.get('/sprite.png')
def sprite(): return send_from_directory(ROOT,'sprite.png')

@app.get('/api/estado')
def estado(): return jsonify(modelo=MODEL)

@app.post('/api/decidir')
def decidir():
    body=request.get_json(silent=True) or {}
    try:
        needs={k:max(0,min(100,float(body.get(k,0)))) for k in ('sed','pipi','cansancio','aburrimiento')}
        if not all(math.isfinite(v) for v in needs.values()): raise ValueError('Valores no finitos')
    except (ValueError,TypeError): return jsonify(error='Necesidades inválidas'),400
    actual=str(body.get('habitacion',''))[:30]
    previo=str(body.get('destino_actual',''))[:30]
    prompt=(f'Actúas como cerebro de un personaje de videojuego. Necesidades (0 satisfecho, 100 urgente): {needs}. '
            f'Habitación actual: {actual}; destino anterior: {previo}. '
            'Habitaciones y necesidades: salon reduce aburrimiento, cocina reduce sed, dormitorio reduce cansancio, bano reduce pipi. '
            'Prioriza necesidades elevadas. Si estás satisfaciendo una necesidad elevada, mantén el destino salvo urgencia mayor. '
            'Elige exactamente una habitación válida y explica brevemente el motivo en español. Devuelve JSON.')
    try:
        r=requests.post(OLLAMA,json={'model':MODEL,'messages':[{'role':'system','content':'Eres un agente de videojuego. Responde exclusivamente JSON válido.'},{'role':'user','content':prompt}],'format':SCHEMA,'stream':False,'options':{'temperature':0.1,'num_predict':140},'keep_alive':'10m'},timeout=90)
        r.raise_for_status()
        import json
        decision=json.loads(r.json()['message']['content'])
        if decision.get('destino') not in ROOMS: raise ValueError('Destino desconocido')
        return jsonify(ok=True,modelo=MODEL,destino=decision['destino'],accion=str(decision.get('accion',''))[:120],motivo=str(decision.get('motivo',''))[:300])
    except (requests.RequestException,ValueError,KeyError,TypeError) as e:
        app.logger.warning('Ollama: %s',e)
        return jsonify(ok=False,error='No se pudo consultar Ollama. Comprueba que está iniciado y que el modelo está descargado.'),503

if __name__=='__main__':
    print('Abre http://127.0.0.1:5000')
    app.run(host='127.0.0.1',port=5000)
