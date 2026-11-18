from flask import Flask, jsonify, request, send_from_directory
import os, sqlite3, json, math, threading, requests
from datetime import datetime, timezone
ROOT=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__,static_folder=None)
MODEL=os.getenv('OLLAMA_MODEL','qwen2.5:7b')
OLLAMA=os.getenv('OLLAMA_URL','http://127.0.0.1:11434/api/chat')
DB=os.path.join(ROOT,'memoria.sqlite')
LOCK=threading.Lock()
ROOMS={'salon':'aburrimiento','cocina':'sed','dormitorio':'cansancio','bano':'pipi'}
WEIGHTS={'sed':1.3,'pipi':1.2,'cansancio':1.,'aburrimiento':.7}
ACTIONS={'salon':'entretenerse','cocina':'beber','dormitorio':'dormir','bano':'ir al WC'}
THOUGHTS={'salon':'Voy a descansar un rato en el salón.','cocina':'Necesito beber agua.','dormitorio':'Voy a dormir un poco.','bano':'Tengo que ir al baño.'}

def connect():
 db=sqlite3.connect(DB,timeout=10);db.row_factory=sqlite3.Row;db.execute('PRAGMA busy_timeout=10000');return db
with connect() as db:
 db.execute('PRAGMA journal_mode=WAL')
 db.execute('''CREATE TABLE IF NOT EXISTS eventos(id INTEGER PRIMARY KEY AUTOINCREMENT,agente_id TEXT NOT NULL DEFAULT 'agente-1',fecha TEXT NOT NULL,tipo TEXT NOT NULL,habitacion TEXT,destino TEXT,accion TEXT,mensaje TEXT,necesidades TEXT)''')
 columns=[r['name'] for r in db.execute('PRAGMA table_info(eventos)')]
 if 'agente_id' not in columns: db.execute("ALTER TABLE eventos ADD COLUMN agente_id TEXT NOT NULL DEFAULT 'agente-1'")
 db.execute('CREATE INDEX IF NOT EXISTS idx_agente_eventos ON eventos(agente_id,id DESC)')

def agent_id(data):
 value=str(data.get('agente_id','agente-1'))
 if not (1<=len(value)<=48 and all(c.isalnum() or c in '-_' for c in value)):raise ValueError('agente_id inválido')
 return value

def needs_of(data):
 result={}
 for k in WEIGHTS:
  v=float(data.get(k,0))
  if not math.isfinite(v):raise ValueError('Necesidad inválida')
  result[k]=round(max(0,min(100,v)),2)
 return result

def remember(kind,data):
 aid=agent_id(data)
 if kind not in ('decision','habla','llegada','bloqueo','accion','inicio'):raise ValueError('Tipo no permitido')
 ns=needs_of(data.get('necesidades') or {})
 with connect() as db:
  db.execute('INSERT INTO eventos(agente_id,fecha,tipo,habitacion,destino,accion,mensaje,necesidades) VALUES(?,?,?,?,?,?,?,?)',(aid,datetime.now(timezone.utc).isoformat(),kind,*[str(data.get(k,'') or '')[:300] for k in ('habitacion','destino','accion','mensaje')],json.dumps(ns)))

def recent(aid,limit=12):
 with connect() as db:return [dict(r) for r in db.execute('SELECT * FROM eventos WHERE agente_id=? ORDER BY id DESC LIMIT ?',(aid,limit))]

@app.get('/')
def index():return send_from_directory(ROOT,'index.html')
@app.get('/sprite.png')
def sprite():return send_from_directory(ROOT,'sprite.png') if os.path.isfile(os.path.join(ROOT,'sprite.png')) else ('',404)
@app.get('/api/estado')
def estado():return jsonify(ok=True,modelo=MODEL,ocupado=LOCK.locked())
@app.get('/api/memoria')
def memoria():
 try:aid=agent_id(request.args);return jsonify(ok=True,eventos=recent(aid,max(1,min(100,int(request.args.get('limit',20))))))
 except (ValueError,TypeError) as e:return jsonify(ok=False,error=str(e)),400
@app.post('/api/evento')
def evento():
 data=request.get_json(silent=True) or {}
 try:remember(data.get('tipo',''),data);return jsonify(ok=True)
 except (ValueError,TypeError) as e:return jsonify(ok=False,error=str(e)),400

@app.post('/api/decidir')
def decidir():
 data=request.get_json(silent=True) or {}
 try:aid=agent_id(data);needs=needs_of(data)
 except (ValueError,TypeError) as e:return jsonify(ok=False,error=str(e)),400
 scores=sorted(((needs[need]*WEIGHTS[need],room,need) for room,need in ROOMS.items() if needs[need]>=12),reverse=True)
 destination=scores[0][1] if scores else 'salon'
 current=data.get('destino_actual')
 if current in ROOMS and needs[ROOMS[current]]>=15 and scores:
  if scores[0][0] <= needs[ROOMS[current]]*WEIGHTS[ROOMS[current]]*1.25+8:destination=current
 action=ACTIONS[destination];thought=THOUGHTS[destination];used=False
 # Una sola generación concurrente; el resto de agentes no se bloquea.
 if LOCK.acquire(blocking=False):
  try:
   history=[{'tipo':e['tipo'],'mensaje':e['mensaje']} for e in reversed(recent(aid,6))]
   prompt=f'Eres {aid}, un personaje. Acción OBLIGATORIA: {action} en {destination}. Necesidades: {json.dumps(needs)}. TU memoria: {json.dumps(history,ensure_ascii=False)}. Escribe una frase breve en primera persona sobre ESA acción exclusivamente. Devuelve JSON {{"motivo":"..."}}.'
   r=requests.post(OLLAMA,json={'model':MODEL,'messages':[{'role':'system','content':'Hablas como personaje de simulación. No cambies la acción. Responde JSON.'},{'role':'user','content':prompt}],'format':{'type':'object','properties':{'motivo':{'type':'string'}},'required':['motivo']},'stream':False,'options':{'temperature':0.3,'num_predict':70},'keep_alive':'20m'},timeout=(3,40));r.raise_for_status()
   candidate=str(json.loads(r.json()['message']['content'])['motivo']).strip()
   forbidden={'salon':['baño','cocina','dormir'],'cocina':['baño','dormir','televisión'],'dormitorio':['baño','cocina','beber'],'bano':['cocina','beber','dormir']}
   if 5<=len(candidate)<=120 and not any(w in candidate.lower() for w in forbidden[destination]):thought=candidate;used=True
  except (requests.RequestException,KeyError,ValueError) as e:app.logger.warning('Ollama: %s',e)
  finally:LOCK.release()
 remember('decision',{'agente_id':aid,'habitacion':data.get('habitacion'),'destino':destination,'accion':action,'mensaje':thought,'necesidades':needs})
 return jsonify(ok=True,agente_id=aid,destino=destination,accion=action,motivo=thought,modelo_respondio=used,prioridades={room:round(needs[need]*WEIGHTS[need],1) for room,need in ROOMS.items()})
if __name__=='__main__':app.run(host='127.0.0.1',port=5000,threaded=True)
