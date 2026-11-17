<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#4f5d95">
<title>JOCARSA | Notificaciones</title>
<style>
:root{--primario:#4f5d95;--fondo:#f4f6fa;--blanco:#fff;--texto:#202638;--secundario:#788196;--borde:#e6e9f0}*{box-sizing:border-box}body{margin:0;background:var(--fondo);color:var(--texto);font-family:system-ui,-apple-system,sans-serif}button,input,select{font:inherit}button{cursor:pointer}button:focus-visible,input:focus-visible{outline:3px solid #e88b2f;outline-offset:2px}.app{max-width:600px;min-height:100dvh;margin:auto;background:white;padding-bottom:calc(85px + env(safe-area-inset-bottom))}.top{position:sticky;top:0;z-index:10;background:white;padding:22px 20px 16px;border-bottom:1px solid var(--borde);display:flex;align-items:center;justify-content:space-between;gap:10px}.top h1{margin:0;font-size:25px}.top p{margin:6px 0 0;color:var(--secundario);font-size:13px}.link{background:none;border:0;color:var(--primario);font-size:13px}.filtros{display:flex;gap:8px;padding:16px 20px}.filtros button{border:0;border-radius:20px;padding:9px 16px;background:var(--fondo);color:var(--secundario);font-size:13px}.filtros button.activo,.primary{background:var(--primario)!important;color:white!important}.agente-filtro{padding:0 20px 14px}.agente-filtro label{display:block;font-size:12px;font-weight:650;color:var(--secundario);margin-bottom:6px}.agente-filtro select{width:100%;padding:11px;border:1px solid var(--borde);border-radius:10px;background:white;color:var(--texto)}.agente-tag{display:block;font-size:11px;font-weight:650;color:var(--primario);margin-top:5px}.detalle{white-space:pre-wrap;color:var(--texto)!important;padding-top:12px;border-top:1px solid var(--borde);margin-top:12px!important}.resumen{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.notificacion.abierta{background:#f9faff}.listado{padding:0 14px}.fecha-grupo{padding:14px 6px 10px;font-size:12px;font-weight:700;color:var(--secundario);text-transform:uppercase;letter-spacing:1px}.notificacion{display:flex;align-items:flex-start;gap:13px;padding:16px 12px;border-bottom:1px solid var(--borde);cursor:pointer;width:100%;text-align:left;background:white;border-left:0;border-right:0;border-top:0}.notificacion.no-leida{background:#f7f8ff}.icono{width:43px;height:43px;flex-shrink:0;border-radius:13px;display:grid;place-items:center;background:#e9edfa;font-size:21px}.contenido{flex:1;min-width:0}.cabecera{display:flex;align-items:baseline;justify-content:space-between;gap:10px}.cabecera h3{margin:0;font-size:15px;font-weight:650}.cabecera time{font-size:11px;color:var(--secundario);white-space:nowrap}.contenido p{margin:6px 0 0;font-size:13px;line-height:1.5;color:var(--secundario);overflow-wrap:anywhere}.punto{width:8px;height:8px;border-radius:50%;background:var(--primario);flex-shrink:0;margin-top:7px}.bottom{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:600px;min-height:72px;display:flex;background:white;border-top:1px solid var(--borde);padding-bottom:env(safe-area-inset-bottom)}.bottom button{flex:1;border:0;background:none;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;color:var(--secundario);font-size:11px}.bottom button span{font-size:22px}.bottom button.activo{color:var(--primario);font-weight:700}.login{max-width:420px;margin:12vh auto 0;padding:30px 24px}.login h1{margin:0 0 8px}.login p{color:var(--secundario);font-size:14px}.campo{display:block;margin:20px 0 8px;font-size:13px;font-weight:650}.entrada{display:block;width:100%;border:1px solid var(--borde);border-radius:10px;padding:13px;background:white}.primary{width:100%;border:0;border-radius:10px;padding:14px;margin-top:22px;font-weight:650}.error{color:#b42318;font-size:13px;min-height:20px}.empty{padding:40px 20px;text-align:center;color:var(--secundario)}[hidden]{display:none!important}@media(min-width:650px){body{padding:30px 0}.app{border-radius:18px;box-shadow:0 10px 40px #20263812;overflow:hidden}}
</style>
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
</head>
<body>
<div class="app">
  <div id="loginView" class="login" hidden>
    <h1>Notificaciones</h1><p>Accede a tu bandeja de avisos.</p>
    <form id="loginForm">
      <label class="campo" for="usuario">Usuario</label>
      <input class="entrada" id="usuario" autocomplete="username" required>
      <label class="campo" for="password">Contraseña</label>
      <input class="entrada" id="password" type="password" autocomplete="current-password" required>
      <button class="primary" type="submit">Iniciar sesión</button>
      <p class="error" id="loginError" role="alert"></p>
    </form>
  </div>
  <div id="appView" hidden>
    <header class="top"><div><h1>Notificaciones</h1><p id="contador">Cargando...</p></div><button class="link" id="salir">Salir</button></header>
    <main><div style="padding:12px 20px 0"><button type="button" id="activarPush" class="primary" style="margin:0" hidden>Activar notificaciones en este dispositivo</button><p id="pushEstado" style="font-size:12px;color:#788196"></p></div><div class="filtros"><button type="button" class="activo" data-filtro="todas">Todas</button><button type="button" data-filtro="no-leidas">No leídas</button></div><div class="agente-filtro"><label for="agenteSelect">Filtrar por agente</label><select id="agenteSelect"><option value="">Todos los agentes</option></select></div><section class="listado" id="listado" aria-live="polite"></section></main>
    <nav class="bottom" aria-label="Navegación principal"><button type="button" id="inicioNav"><span>⌂</span>Inicio</button><button type="button" class="activo" id="avisosNav"><span>🔔</span>Avisos</button><button type="button" id="perfilNav"><span>👤</span>Perfil</button></nav>
  </div>
</div>
<script>
'use strict';
const STORAGE_KEY='jocarsa_notificaciones_auth_v3';
let token=localStorage.getItem(STORAGE_KEY)||'';
let notificaciones=[];
let filtro='todas';
let agenteFiltro='';
const abiertos=new Set();
let cargando=false;
const $=id=>document.getElementById(id);
function mostrarLogin(mensaje=''){$('loginView').hidden=false;$('appView').hidden=true;$('loginError').textContent=mensaje;}
function mostrarApp(){$('loginView').hidden=true;$('appView').hidden=false;}
async function api(accion,datos=null){
 const options={method:datos===null?'GET':'POST',headers:{'Content-Type':'application/json'}};
 if(token) options.headers['X-Session-Token']=token;
 if(datos!==null) options.body=JSON.stringify({...datos,accion});
 const res=await fetch('api.php'+(datos===null?'?accion='+encodeURIComponent(accion):''),options);
 const json=await res.json();
 if(!res.ok) {const error=new Error(json.error||'Error HTTP '+res.status);error.status=res.status;throw error;}
 return json;
}
function fechaLocal(iso){const s=iso.replace(' ','T')+'Z';return new Date(s);}
function grupoFecha(iso){const d=fechaLocal(iso);if(Number.isNaN(d.getTime()))return 'Anterior';const hoy=new Date();const dia=new Date(hoy.getFullYear(),hoy.getMonth(),hoy.getDate());const n=new Date(d.getFullYear(),d.getMonth(),d.getDate());const dif=Math.round((dia-n)/86400000);if(dif===0)return 'Hoy';if(dif===1)return 'Ayer';return new Intl.DateTimeFormat('es-ES',{day:'numeric',month:'long',year:'numeric'}).format(d);}
async function cargarAgentes(){
 const r=await api('agentes');const sel=$('agenteSelect');const anterior=sel.value;
 sel.replaceChildren(new Option('Todos los agentes',''));
 for(const a of r.agentes)sel.add(new Option(a.nombre+' ('+a.total+')',a.clave));
 if(notificaciones.some(n=>!n.agente_clave))sel.add(new Option('Sin agente','__sin_agente__'));
 sel.value=anterior;
}
function render(){
 const sinLeer=notificaciones.filter(n=>!Number(n.leida)).length;
 $('contador').textContent=sinLeer===1?'1 notificación sin leer':sinLeer+' notificaciones sin leer';
 const root=$('listado');root.replaceChildren();let ultimo='';let visibles=0;
 for(const n of notificaciones){if(filtro==='no-leidas'&&Number(n.leida))continue;if(agenteFiltro && (n.agente_clave||'__sin_agente__')!==agenteFiltro)continue;visibles++;
  const grupo=grupoFecha(n.creada);if(grupo!==ultimo){const h=document.createElement('div');h.className='fecha-grupo';h.textContent=grupo;root.append(h);ultimo=grupo;}
  const article=document.createElement('button');article.type='button';article.className='notificacion'+(!Number(n.leida)?' no-leida':'');
  const ico=document.createElement('div');ico.className='icono';ico.textContent=n.icono;
  const content=document.createElement('div');content.className='contenido';const head=document.createElement('div');head.className='cabecera';const title=document.createElement('h3');title.textContent=n.titulo;const time=document.createElement('time');time.dateTime=n.creada;const date=fechaLocal(n.creada);time.textContent=Number.isNaN(date.getTime())?'':new Intl.DateTimeFormat('es-ES',{hour:'2-digit',minute:'2-digit'}).format(date);head.append(title,time);const tag=document.createElement('span');tag.className='agente-tag';tag.textContent=n.agente_nombre;const p=document.createElement('p');p.className='resumen';p.textContent=n.descripcion.split('\n').find(x=>x.trim())||n.descripcion;content.append(head,tag,p);if(abiertos.has(Number(n.id))){article.classList.add('abierta');const detalle=document.createElement('p');detalle.className='detalle';detalle.textContent=n.descripcion;content.append(detalle);}article.append(ico,content);
  if(!Number(n.leida)){const punto=document.createElement('span');punto.className='punto';article.append(punto);}
  article.addEventListener('click',async()=>{const id=Number(n.id);if(abiertos.has(id))abiertos.delete(id);else abiertos.add(id);if(!Number(n.leida)){try{await api('leer',{id});n.leida=1;}catch(e){alert(e.message);}}render();});
  root.append(article);
 }
 if(!visibles){const p=document.createElement('p');p.className='empty';p.textContent='No hay notificaciones para mostrar.';root.append(p);}
}
async function cargar(){if(!token||cargando)return;cargando=true;try{const r=await api('listar');notificaciones=r.notificaciones;await cargarAgentes();mostrarApp();render();}catch(e){if(e.status===401){token='';localStorage.removeItem(STORAGE_KEY);mostrarLogin('La sesión ha caducado. Inicia sesión.');}else{$('contador').textContent='No se pudo actualizar: '+e.message;}}finally{cargando=false;}}
$('loginForm').addEventListener('submit',async e=>{e.preventDefault();$('loginError').textContent='';const btn=e.submitter;btn.disabled=true;try{const r=await api('login',{usuario:$('usuario').value.trim(),password:$('password').value});token=r.token;localStorage.setItem(STORAGE_KEY,token);$('password').value='';mostrarApp();await cargar();await prepararPWA();}catch(err){$('loginError').textContent=err.message;}finally{btn.disabled=false;}});
$('salir').addEventListener('click',async()=>{try{await api('logout',{});}catch(e){}token='';localStorage.removeItem(STORAGE_KEY);notificaciones=[];mostrarLogin();});
document.querySelectorAll('[data-filtro]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-filtro]').forEach(x=>x.classList.remove('activo'));b.classList.add('activo');filtro=b.dataset.filtro;render();}));
$('agenteSelect').addEventListener('change',e=>{agenteFiltro=e.target.value;render();});
$('inicioNav').addEventListener('click',()=>{filtro='todas';document.querySelector('[data-filtro="todas"]').click();window.scrollTo({top:0,behavior:'smooth'});});
$('avisosNav').addEventListener('click',()=>cargar());
$('perfilNav').addEventListener('click',async()=>{const actual=prompt('Contraseña actual (Cancelar para salir):');if(actual===null)return;const nueva=prompt('Nueva contraseña (mínimo 12 caracteres):');if(nueva===null)return;try{await api('cambiar_password',{actual,nueva});token='';localStorage.removeItem(STORAGE_KEY);mostrarLogin('Contraseña cambiada. Vuelve a entrar.');}catch(e){alert(e.message);}});
async function prepararPWA(){
 if(!('serviceWorker' in navigator))return;
 try {await navigator.serviceWorker.register('./sw.js');}catch(e){console.warn('Service Worker:',e);return;}
 if(!('PushManager' in window)||!('Notification' in window)){$('pushEstado').textContent='Este navegador no admite notificaciones push.';return;}
 try {const r=await api('push_config');if(!r.disponible){$('pushEstado').textContent='Push pendiente de configurar en el servidor (VAPID y Composer).';return;}
 const reg=await navigator.serviceWorker.ready;const existente=await reg.pushManager.getSubscription();
 if(existente){await api('push_suscribir',{subscription:existente.toJSON()});$('pushEstado').textContent='Notificaciones push activadas.';return;}
 $('activarPush').hidden=false;
 }catch(e){console.warn('Push:',e);}
}
function urlBase64ToUint8Array(base64){const p='='.repeat((4-base64.length%4)%4);const raw=atob((base64+p).replace(/-/g,'+').replace(/_/g,'/'));return Uint8Array.from([...raw].map(c=>c.charCodeAt(0)));}
$('activarPush').addEventListener('click',async()=>{try{
 const permiso=await Notification.requestPermission();if(permiso!=='granted')throw Error('Permiso de notificaciones denegado');
 const config=await api('push_config');if(!config.disponible)throw Error('Push no configurado en el servidor');
 const reg=await navigator.serviceWorker.ready;
 const sub=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:urlBase64ToUint8Array(config.publicKey)});
 await api('push_suscribir',{subscription:sub.toJSON()});$('activarPush').hidden=true;$('pushEstado').textContent='Notificaciones push activadas.';
 }catch(e){$('pushEstado').textContent=e.message;}});
if('serviceWorker' in navigator)navigator.serviceWorker.addEventListener('message',e=>{if(e.data?.type==='abrir-notificacion')cargar();});
if(token){mostrarApp();cargar().then(prepararPWA);}else mostrarLogin();
setInterval(()=>{if(token&&!document.hidden)cargar();},15000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&token)cargar();});
</script>
</body>
</html>
