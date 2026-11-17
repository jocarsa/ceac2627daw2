const $=s=>document.querySelector(s);let csrf='',current=null,busy=false,register=false,version=0;
async function api(accion,data={}){const r=await fetch('servidor.php?accion='+encodeURIComponent(accion),{method:accion==='sesion'?'GET':'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},...(accion==='sesion'?{}:{body:JSON.stringify(data)})});const j=await r.json();if(!r.ok)throw Error(j.error||'Error de conexión');return j;}
function error(e){alert(e.message||String(e));}
function showAuth(){ $('#auth').hidden=false;$('#app').hidden=true; }
function showApp(user,token){csrf=token;$('#auth').hidden=true;$('#app').hidden=false;$('#profile-name').textContent=user.nombre;$('#avatar').textContent=user.nombre.charAt(0).toUpperCase();loadList();}
function setRegister(value){register=value;$('#register-fields').hidden=!value;$('#tab-login').classList.toggle('selected',!value);$('#tab-registro').classList.toggle('selected',value);$('#auth-submit').textContent=value?'Crear cuenta':'Entrar';$('#auth-error').textContent='';$('#auth-form').elements.contrasena.autocomplete=value?'new-password':'current-password';}
$('#tab-login').onclick=()=>setRegister(false);$('#tab-registro').onclick=()=>setRegister(true);
$('#auth-form').onsubmit=async e=>{e.preventDefault();const b=Object.fromEntries(new FormData(e.currentTarget));$('#auth-submit').disabled=true;try{const d=await api(register?'registro':'login',b);e.currentTarget.reset();showApp(d.usuario,d.csrf);}catch(err){$('#auth-error').textContent=err.message;}finally{$('#auth-submit').disabled=false;}};
function closeSide(){$('#entities-panel').classList.remove('open');$('#superentities').classList.remove('open');$('#shade').classList.remove('visible');}
$('#open-side').onclick=()=>{$('#superentities').classList.add('open');$('#entities-panel').classList.add('open');$('#shade').classList.add('visible');};$('#close-side').onclick=closeSide;$('#shade').onclick=closeSide;
$('#theme').onclick=()=>{document.body.classList.toggle('light');localStorage.setItem('ia-theme',document.body.classList.contains('light')?'light':'dark');};if(localStorage.getItem('ia-theme')==='light')document.body.classList.add('light');
async function loadList(){const d=await api('listar');const list=$('#conversations');list.replaceChildren();for(const c of d.conversaciones){const row=document.createElement('div');row.className='conversation'+(current===c.id?' active':'');const btn=document.createElement('button');btn.className='conversation-title';btn.textContent='◷  '+(c.titulo||'Sin título');btn.title=c.titulo;btn.onclick=()=>openChat(c.id);const del=document.createElement('button');del.className='delete-chat';del.textContent='×';del.title='Eliminar conversación';del.onclick=async()=>{if(!confirm('¿Eliminar esta conversación y sus mensajes?'))return;try{await api('eliminar',{id:c.id});if(current===c.id){current=null;version++;renderEmpty();}await loadList();}catch(e){error(e);}};row.append(btn,del);list.append(row);}}
function renderEmpty(){ $('#messages').replaceChildren();$('#welcome').hidden=false;$('#current-title').textContent='Nueva conversación';}
async function openChat(id){if(busy)return;current=id;const v=++version;closeSide();try{const d=await api('mensajes',{id});if(v!==version)return;$('#current-title').textContent=d.titulo;$('#messages').replaceChildren();$('#welcome').hidden=d.mensajes.length>0;for(const m of d.mensajes)addMessage(m.emisor,m.mensaje);await loadList();scrollBottom();}catch(e){error(e);}}
async function newChat(){if(busy)return;try{const d=await api('crear');await openChat(d.id);$('#message').focus();}catch(e){error(e);}}
$('#new').onclick=newChat;
$('#rename').onclick=async()=>{if(!current)return;const title=prompt('Nuevo título de la conversación',$('#current-title').textContent);if(!title||!title.trim())return;try{await api('renombrar',{id:current,titulo:title.trim()});$('#current-title').textContent=title.trim();await loadList();}catch(e){error(e);}};
$('#logout').onclick=async()=>{if(busy)return;try{await api('logout');csrf='';current=null;version++;showAuth();}catch(e){error(e);}};
function addMessage(role,text){const item=document.createElement('article');item.className='message '+(role==='usuario'?'user':'assistant');const icon=document.createElement('div');icon.className='message-avatar';icon.textContent=role==='usuario'?$('#avatar').textContent:'✦';const content=document.createElement('div');content.className='message-content';content.textContent=text;item.append(icon,content);$('#messages').append(item);$('#welcome').hidden=true;scrollBottom();return item;}
function scrollBottom(){$('#scroll').scrollTop=$('#scroll').scrollHeight;}
function setBusy(value){busy=value;$('#send').disabled=value;$('#message').disabled=value;$('#new').disabled=value;}
$('#composer').onsubmit=async e=>{e.preventDefault();const text=$('#message').value.trim();if(!text||busy)return;try{if(!current){const d=await api('crear');current=d.id;version++;}const id=current;$('#message').value='';resize();addMessage('usuario',text);setBusy(true);const typing=addMessage('ia','Pensando…');typing.classList.add('typing');try{const d=await api('enviar',{id,mensaje:text});typing.remove();if(current===id)addMessage('ia',d.respuesta);await loadList();const c=await api('mensajes',{id});if(current===id)$('#current-title').textContent=c.titulo;}catch(err){typing.remove();addMessage('ia','No se ha podido completar la respuesta: '+err.message);}finally{setBusy(false);$('#message').focus();}}catch(err){error(err);}};
function resize(){const el=$('#message');el.style.height='auto';el.style.height=Math.min(el.scrollHeight,200)+'px';}$('#message').addEventListener('input',resize);$('#message').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('#composer').requestSubmit();}});
document.querySelectorAll('[data-prompt]').forEach(b=>b.onclick=()=>{$('#message').value=b.dataset.prompt;resize();$('#message').focus();});
api('sesion').then(d=>{if(d.usuario)showApp(d.usuario,d.csrf);else showAuth();}).catch(()=>showAuth());


// Navegación por superentidades: columna 1 -> columna 2 -> escenario.
let activeSuper='conversaciones';
const sectionNames={conversaciones:'Conversaciones',proyectos:'Proyectos',biblioteca:'Biblioteca'};
function chooseSuper(key){
 activeSuper=key;
 document.querySelectorAll('[data-super]').forEach(b=>{b.classList.toggle('selected',b.dataset.super===key);b.setAttribute('aria-current',b.dataset.super===key?'page':'false');});
 document.querySelector('.side-label').textContent=sectionNames[key].toUpperCase();
 const chats= document.querySelector('#conversations'), add=document.querySelector('#new'), placeholder=document.querySelector('#section-placeholder');
 const isChat=key==='conversaciones';chats.hidden=!isChat;add.hidden=!isChat;placeholder.hidden=isChat;
 if(!isChat){placeholder.replaceChildren();const note=document.createElement('div');note.className='entity-empty';note.textContent=key==='proyectos'?'Los proyectos aparecerán aquí cuando se implemente su gestión.':'Los elementos de la biblioteca aparecerán aquí cuando se implemente su gestión.';placeholder.append(note);}
 document.querySelector('#composer-wrap-placeholder')?.remove();
 document.querySelector('#app main').classList.toggle('inactive-section',!isChat);
 const stage=document.querySelector('#stage-placeholder');if(stage){stage.hidden=isChat;stage.querySelector('h2').textContent=sectionNames[key];stage.querySelector('p').textContent='Sección reservada para futuras funcionalidades.';}
 closeSide();
}
document.querySelectorAll('[data-super]').forEach(b=>b.addEventListener('click',()=>chooseSuper(b.dataset.super)));
