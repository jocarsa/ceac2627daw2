from flask import Flask, jsonify, request, send_from_directory
import os, requests, math, json, threading, time, sqlite3
from datetime import datetime, timezone
ROOT=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__,static_folder=None)
MODEL=os.getenv('OLLAMA_MODEL','qwen2.5:3b')
OLLAMA=os.getenv('OLLAMA_URL','http://127.0.0.1:11434/api/chat')
DB=os.getenv('MEMORY_DB',os.path.join(ROOT,'memoria.sqlite'))
ROOMS={'salon':'aburrimiento','cocina':'sed','dormitorio':'cansancio','bano':'pipi'}
SCHEMA={'type':'object','properties':{'destino':{'type':'string','enum':list(ROOMS)},'accion':{'type':'string'},'motivo':{'type':'string'}},'required':['destino','accion','motivo']}
LOCK=threading.Lock()
def connect():
    db=sqlite3.connect(DB,timeout=10)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA busy_timeout=10000')
    return db
def init():
    with connect() as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('''CREATE TABLE IF NOT EXISTS eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, tipo TEXT NOT NULL, habitacion TEXT, destino TEXT, accion TEXT, mensaje TEXT, necesidades TEXT)''')
        db.execute('CREATE INDEX IF NOT EXISTS idx_eventos_fecha ON eventos(id DESC)')
init()
def remember(tipo,body):
    if tipo not in ('decision','habla','llegada','bloqueo','accion','inicio'): raise ValueError('tipo no permitido')
    def clean(k,n=200): return str(body.get(k,'') or '')[:n]
    needs={k:round(max(0,min(100,float(body.get('necesidades',{}).get(k,0)))),1) for k in ('sed','pipi','cansancio','aburrimiento')}
    with connect() as db:
        cur=db.execute('INSERT INTO eventos(fecha,tipo,habitacion,destino,accion,mensaje,necesidades) VALUES(?,?,?,?,?,?,?)', (datetime.now(timezone.utc).isoformat(),tipo,clean('habitacion',40),clean('destino',40),clean('accion',120),clean('mensaje',300),json.dumps(needs)))
        return cur.lastrowid
def recent(limit=12):
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT id,fecha,tipo,habitacion,destino,accion,mensaje,necesidades FROM eventos ORDER BY id DESC LIMIT ?', (limit,))]
@app.get('/')
def index():return send_from_directory(ROOT,'index.html')
@app.get('/sprite.png')
def sprite():return send_from_directory(ROOT,'sprite.png') if os.path.isfile(os.path.join(ROOT,'sprite.png')) else ('',404)
@app.get('/api/memoria')
def memoria():
    limit=max(1,min(100,int(request.args.get('limit',20))))
    return jsonify(ok=True,eventos=recent(limit))
@app.post('/api/evento')
def evento():
    data=request.get_json(silent=True) or {}
    try: return jsonify(ok=True,id=remember(data.get('tipo',''),data))
    except (ValueError,TypeError,AttributeError) as e:return jsonify(ok=False,error=str(e)),400
@app.get('/api/estado')
def estado():
    try:
        r=requests.get(OLLAMA.replace('/api/chat','/api/tags'),timeout=3);r.raise_for_status()
        names=[m.get('name','') for m in r.json().get('models',[])]
        return jsonify(ok=True,modelo=MODEL,disponible=MODEL in names,modelos=names,ocupado=LOCK.locked(),memoria=DB)
    except requests.RequestException as e:return jsonify(ok=False,error=str(e)),503
@app.post('/api/decidir')
def decidir():
    body=request.get_json(silent=True) or {}
    try:
        needs={k:max(0,min(100,float(body.get(k,0)))) for k in ('sed','pipi','cansancio','aburrimiento')}
        if not all(math.isfinite(v) for v in needs.values()):raise ValueError()
    except (ValueError,TypeError):return jsonify(ok=False,error='Necesidades inválidas'),400
    if not LOCK.acquire(blocking=False):return jsonify(ok=False,ocupado=True,error='Ollama ocupado'),429
    try:
        history=recent(10)
        summary=[{'tipo':e['tipo'],'lugar':e['habitacion'],'destino':e['destino'],'mensaje':e['mensaje']} for e in reversed(history)]
        prompt=(f'Necesidades (0 satisfecho, 100 urgente): {needs}. '
                f'Habitación: {str(body.get("habitacion",""))[:40]}; destino actual: {str(body.get("destino_actual",""))[:40]}. '
                f'Memoria reciente de acciones y frases: {json.dumps(summary,ensure_ascii=False)}. '
                'Eres un personaje de videojuego con memoria. Elige el destino que atienda la necesidad más urgente, '
                'sin cambiar innecesariamente de destino. salon=aburrimiento, cocina=sed, dormitorio=cansancio, bano=pipi. '
                'Responde JSON: destino, accion, motivo. Motivo en primera persona, natural, máximo 18 palabras.')
        try:
            r=requests.post(OLLAMA,json={'model':MODEL,'messages':[{'role':'system','content':'Eres un personaje autónomo. Responde JSON válido.'},{'role':'user','content':prompt}],'format':SCHEMA,'stream':False,'options':{'temperature':0.2,'num_predict':130},'keep_alive':'20m'},timeout=(5,120))
            r.raise_for_status();data=json.loads(r.json()['message']['content'])
            if data.get('destino') not in ROOMS:raise ValueError('Destino inválido')
            result={'modelo':MODEL,'destino':data['destino'],'accion':str(data.get('accion',''))[:120],'motivo':str(data.get('motivo',''))[:200]}
            remember('decision',{'habitacion':body.get('habitacion'),'destino':result['destino'],'accion':result['accion'],'mensaje':result['motivo'],'necesidades':needs})
            return jsonify(ok=True,**result)
        except (requests.RequestException,ValueError,KeyError,TypeError) as e:
            app.logger.exception('Fallo Ollama')
            return jsonify(ok=False,error=str(e)),503
    finally:LOCK.release()
if __name__=='__main__':
    print('Casa IA v4 |',MODEL,'| SQLite:',DB)
    app.run(host='127.0.0.1',port=5000,threaded=True)
