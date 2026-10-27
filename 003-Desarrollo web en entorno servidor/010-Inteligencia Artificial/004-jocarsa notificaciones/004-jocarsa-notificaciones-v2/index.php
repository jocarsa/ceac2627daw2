<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#4f5d95">
<title>Notificaciones | JOCARSA</title>
<style>
:root{--primario:#4f5d95;--fondo:#f4f6fa;--texto:#202638;--secundario:#788196;--borde:#e6e9f0}*{box-sizing:border-box}body{margin:0;background:var(--fondo);color:var(--texto);font-family:system-ui,sans-serif}button,input{font:inherit}button{cursor:pointer}button:focus-visible,input:focus-visible{outline:2px solid #e88b2f;outline-offset:2px}.app{max-width:600px;min-height:100dvh;margin:auto;background:#fff;padding-bottom:calc(80px + env(safe-area-inset-bottom))}header{position:sticky;top:0;z-index:10;background:white;padding:22px 20px 16px;border-bottom:1px solid var(--borde);display:flex;justify-content:space-between;align-items:center;gap:10px}h1{margin:0;font-size:25px}header p{margin:6px 0 0;font-size:13px;color:var(--secundario)}.small-btn{background:#eef0f7;border:0;color:var(--primario);border-radius:10px;padding:9px}.filtros{display:flex;gap:8px;padding:16px 20px}.filtros button{border:0;border-radius:20px;padding:9px 16px;background:var(--fondo);color:var(--secundario);font-size:13px}.filtros button.activo{background:var(--primario);color:white}section{padding:0 14px}.fecha-grupo{padding:14px 6px 10px;font-size:12px;font-weight:700;color:var(--secundario);text-transform:uppercase;letter-spacing:1px}article{display:flex;align-items:flex-start;gap:13px;padding:16px 12px;border-bottom:1px solid var(--borde);cursor:pointer}article.no-leida{background:#f7f8ff}article:focus-visible{outline:2px solid var(--primario)}.icono{width:43px;height:43px;flex-shrink:0;border-radius:13px;display:grid;place-items:center;background:#e9edfa;font-size:21px}.contenido{flex:1;min-width:0}.cabecera{display:flex;align-items:baseline;justify-content:space-between;gap:10px}h3{margin:0;font-size:15px}time{font-size:11px;color:var(--secundario);white-space:nowrap}article p{margin:6px 0 0;font-size:13px;line-height:1.5;color:var(--secundario);overflow-wrap:anywhere}.punto{width:8px;height:8px;border-radius:50%;background:var(--primario);flex-shrink:0;margin-top:7px}nav{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:600px;min-height:72px;display:flex;background:#fff;border-top:1px solid var(--borde);padding-bottom:env(safe-area-inset-bottom)}nav a{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;text-decoration:none;color:var(--secundario);font-size:11px}nav a span{font-size:22px}nav a.activo{color:var(--primario);font-weight:700}.login{min-height:100dvh;display:grid;place-items:center;padding:20px}.login form{background:white;padding:28px;border-radius:18px;width:min(100%,380px);box-shadow:0 10px 40px #20263812}.login h1{margin-bottom:20px}.login label{display:block;margin:12px 0 5px;font-size:13px}.login input{width:100%;padding:12px;border:1px solid var(--borde);border-radius:10px}.primary{background:var(--primario);color:white;border:0;padding:12px;border-radius:10px;width:100%;margin-top:18px}.error{color:#b42318;font-size:13px}.empty{padding:35px 15px;text-align:center;color:var(--secundario)}[hidden]{display:none!important}@media(min-width:650px){body{padding:30px 0}.app{border-radius:18px;box-shadow:0 10px 40px #20263812;overflow:hidden}}
</style>
</head>
<body>
<div class="login" id="loginPanel">
<form id="loginForm">
<h1>JOCARSA | Avisos</h1>
<label for="usuario">Usuario</label><input id="usuario" autocomplete="username" required>
<label for="password">Contraseña</label><input id="password" type="password" autocomplete="current-password" required>
<button class="primary" type="submit">Entrar</button><p class="error" id="loginError" role="alert"></p>
</form>
</div>
<div class="app" id="app" hidden>
<header><div><h1>Notificaciones</h1><p id="contador">Cargando...</p></div><button class="small-btn" id="salir">Salir</button></header>
<main><div class="filtros"><button class="activo" data-filtro="todas">Todas</button><button data-filtro="no-leidas">No leídas</button></div><section id="lista" aria-live="polite"></section></main>
<nav aria-label="Navegación principal"><a href="#inicio"><span>⌂</span>Inicio</a><a href="#notificaciones" class="activo" aria-current="page"><span>🔔</span>Avisos</a><a href="#perfil"><span>👤</span>Perfil</a></nav>
</div>
<script>
const $=id=>document.getElementById(id);
let token=localStorage.getItem('jocarsa_avisos_sesion_v2_20261027')||'';
let mensajes=[];
let filtro='todas';
async function api(accion,datos=null){
 const res=await fetch('api.php'+(datos===null?'?accion='+encodeURIComponent(accion):''),{
  method:datos===null?'GET':'POST',headers:{'Content-Type':'application/json',...(token&&accion!=='login'?{'Authorization':'Bearer '+token}:{})},
  ...(datos===null?{}:{body:JSON.stringify({accion,...datos})}),cache:'no-store'
 });
 const body=await res.json();if(!res.ok){const error=new Error(body.error||'Error de conexión');error.status=res.status;throw error;}return body;
}
function sesion(activa){$('app').hidden=!activa;$('loginPanel').hidden=activa;}
function fechaGrupo(fecha){const d=new Date(fecha.replace(' ','T')+'Z');if(isNaN(d))return 'Sin fecha';const hoy=new Date();const a=new Date(hoy.getFullYear(),hoy.getMonth(),hoy.getDate());const b=new Date(d.getFullYear(),d.getMonth(),d.getDate());const dias=Math.round((a-b)/86400000);return dias===0?'Hoy':dias===1?'Ayer':new Intl.DateTimeFormat('es-ES',{dateStyle:'long'}).format(d);}
function render(){
 const lista=$('lista');lista.replaceChildren();const sinLeer=mensajes.filter(m=>!Number(m.leida)).length;
 $('contador').textContent=sinLeer===1?'1 notificación sin leer':sinLeer+' notificaciones sin leer';
 const visibles=mensajes.filter(m=>filtro==='todas'||!Number(m.leida));
 if(!visibles.length){const e=document.createElement('p');e.className='empty';e.textContent='No hay notificaciones';lista.append(e);return;}
 let grupo='';
 for(const m of visibles){const g=fechaGrupo(m.fecha);if(g!==grupo){grupo=g;const h=document.createElement('div');h.className='fecha-grupo';h.textContent=g;lista.append(h);}
 const art=document.createElement('article');art.tabIndex=0;art.setAttribute('role','button');if(!Number(m.leida))art.className='no-leida';
 const ico=document.createElement('div');ico.className='icono';ico.textContent=m.icono;
 const contenido=document.createElement('div');contenido.className='contenido';const cab=document.createElement('div');cab.className='cabecera';
 const titulo=document.createElement('h3');titulo.textContent=m.titulo;const hora=document.createElement('time');hora.dateTime=m.fecha;hora.textContent=m.fecha.slice(11,16);cab.append(titulo,hora);
 const desc=document.createElement('p');desc.textContent=m.descripcion;contenido.append(cab,desc);art.append(ico,contenido);
 if(!Number(m.leida)){const punto=document.createElement('span');punto.className='punto';art.append(punto);}
 const leer=async()=>{if(Number(m.leida))return;try{await api('leer',{id:m.id});m.leida=1;render();}catch(e){alert(e.message)}};
 art.addEventListener('click',leer);art.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();leer();}});lista.append(art);
 }
}
async function cargar(){if(!token)return;try{mensajes=(await api('listar')).notificaciones;render();}catch(e){if(e.status===401){token='';localStorage.removeItem('jocarsa_avisos_sesion_v2_20261027');sesion(false)}else $('contador').textContent=e.message;}}
$('loginForm').addEventListener('submit',async e=>{e.preventDefault();$('loginError').textContent='';try{const r=await api('login',{usuario:$('usuario').value,password:$('password').value});token=r.token;localStorage.setItem('jocarsa_avisos_sesion_v2_20261027',token);$('password').value='';sesion(true);await cargar();}catch(err){$('loginError').textContent=err.message;}});
$('salir').addEventListener('click',async()=>{try{await api('logout',{})}catch(e){}token='';localStorage.removeItem('jocarsa_avisos_sesion_v2_20261027');sesion(false)});
document.querySelectorAll('.filtros button').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.filtros button').forEach(x=>x.classList.remove('activo'));b.classList.add('activo');filtro=b.dataset.filtro;render();}));
if(token){sesion(true);cargar()}else sesion(false);
setInterval(()=>{if(token&&!document.hidden)cargar()},15000);
</script>
</body>
</html>
