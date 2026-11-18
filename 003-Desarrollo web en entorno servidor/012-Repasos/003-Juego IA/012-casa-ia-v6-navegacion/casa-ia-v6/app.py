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
# Prioridades y acciones validadas por el servidor.
WEIGHTS={'sed':1.3,'pipi':1.2,'cansancio':1.0,'aburrimiento':0.7}
ACTIONS={'cocina':'beber','bano':'ir al WC','dormitorio':'dormir','salon':'entretenerse'}
THOUGHTS={'cocina':'Tengo sed. Voy a la cocina a beber.',
          'bano':'Necesito ir al baño.',
          'dormitorio':'Estoy cansado. Voy a dormir.',
          'salon':'Me aburro. Voy a entretenerme en el salón.'}
NEED_FOR_ROOM={room:need for room,need in ROOMS.items()}

@app.post('/api/decidir')
def decidir():
    body=request.get_json(silent=True) or {}
    try:
        needs={k:max(0,min(100,float(body.get(k,0)))) for k in WEIGHTS}
        if not all(math.isfinite(v) for v in needs.values()):raise ValueError()
    except (ValueError,TypeError):return jsonify(ok=False,error='Necesidades inválidas'),400

    # No se permite elegir una necesidad satisfecha si hay otras pendientes.
    options=sorted(((needs[need]*WEIGHTS[need],room,need) for room,need in ROOMS.items()
                    if needs[need]>=12),reverse=True)
    current=str(body.get('destino_actual') or '')
    if options:
        score,destination,need=options[0]
        # Histéresis: mantener la tarea si sigue siendo relevante y
        # ninguna alternativa supera su prioridad en un 25% + 8 puntos.
        if current in ROOMS and needs[ROOMS[current]]>=15:
            current_score=needs[ROOMS[current]]*WEIGHTS[ROOMS[current]]
            if score<=current_score*1.25+8:
                destination=current
    else:
        destination='salon'  # reposo / actividad libre sin necesidad urgente
    action=ACTIONS[destination]
    thought=THOUGHTS[destination]
    model_used=False
    # Ollama redacta la frase, NO controla el destino. Si falla, el juego sigue.
    if LOCK.acquire(blocking=False):
        try:
            summary=[{'tipo':e['tipo'],'destino':e['destino'],'mensaje':e['mensaje']}
                     for e in reversed(recent(6))]
            prompt=(f'Necesidades: {json.dumps(needs,ensure_ascii=False)}. '
                    f'Decisión obligatoria ya validada: destino={destination}, accion={action}. '
                    f'Memoria: {json.dumps(summary,ensure_ascii=False)}. '
                    'Escribe una sola frase breve en primera persona explicando '
                    'EXCLUSIVAMENTE esa acción. No menciones otras necesidades. '
                    'Devuelve JSON con campo motivo.')
            r=requests.post(OLLAMA,json={'model':MODEL,'messages':[
                {'role':'system','content':'Eres un personaje de videojuego. No cambies la acción decidida. Responde JSON.'},
                {'role':'user','content':prompt}],
                'format':{'type':'object','properties':{'motivo':{'type':'string'}},'required':['motivo']},
                'stream':False,'options':{'temperature':0.15,'num_predict':80},'keep_alive':'20m'},timeout=(3,35))
            r.raise_for_status()
            candidate=str(json.loads(r.json()['message']['content']).get('motivo','')).strip()
            # No aceptamos frases que contradigan la acción validada.
            forbidden={'cocina':['baño','dormir','televisión'],
                       'bano':['cocina','beber','dormir'],
                       'dormitorio':['baño','cocina','beber'],
                       'salon':['baño','cocina','dormir']}
            if 5<=len(candidate)<=125 and not any(w in candidate.lower() for w in forbidden[destination]):
                thought=candidate;model_used=True
        except (requests.RequestException,ValueError,KeyError,TypeError, json.JSONDecodeError) as e:
            app.logger.warning('Ollama no disponible; decisión local: %s',e)
        finally:
            LOCK.release()
    result={'ok':True,'modelo':MODEL,'destino':destination,'accion':action,
            'motivo':thought,'modelo_respondio':model_used,
            'prioridades':{room:round(needs[need]*WEIGHTS[need],1) for room,need in ROOMS.items()}}
    remember('decision',{'habitacion':body.get('habitacion'),'destino':destination,
                        'accion':action,'mensaje':thought,'necesidades':needs})
    return jsonify(result)

if __name__=='__main__':
    print('Casa IA v4 |',MODEL,'| SQLite:',DB)
    app.run(host='127.0.0.1',port=5000,threaded=True)
