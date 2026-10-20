const plantilla = document.querySelector('#publicacion');
const contenedor = document.querySelector('#publicaciones');
const TAMANO = 10;
const MAXIMO = 30;
const UMBRAL = 700;

let inicio = 0;
let fin = 0;
let finalAlcanzado = false;
let cargando = false;
let ultimaPosicion = window.scrollY;
const alturas = new Map();
const superior = document.createElement('div');
const inferior = document.createElement('div');
superior.className = inferior.className = 'espaciador';
contenedor.append(superior, inferior);

async function solicitar(offset, limite = TAMANO) {
    const respuesta = await fetch(`api.php?offset=${offset}&limite=${limite}`);
    if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status}`);
    const datos = await respuesta.json();
    if (!Array.isArray(datos)) throw new Error('JSON no válido');
    return datos;
}
function crear(dato, indice) {
    const fragmento = plantilla.content.cloneNode(true);
    const articulo = fragmento.querySelector('article');
    articulo.dataset.indice = indice;
    articulo.dataset.id = dato.id;
    articulo.querySelector('p').textContent = dato.contenidos;
    return fragmento;
}
function articulos() {
    return Array.from(contenedor.querySelectorAll(':scope > article'));
}
function gap() {
    return parseFloat(getComputedStyle(contenedor).rowGap) || 0;
}
function medir() {
    for (const articulo of articulos()) {
        alturas.set(Number(articulo.dataset.indice), articulo.getBoundingClientRect().height);
    }
}
function espacio(desde, hasta) {
    let suma = 0;
    for (let i = desde; i < hasta; i++) suma += (alturas.get(i) || 140) + gap();
    return suma;
}
let totalConocido = 0;
function actualizarEspaciadores() {
    superior.style.height = `${espacio(0, inicio)}px`;
    inferior.style.height = `${espacio(fin, totalConocido)}px`;
}
function recortarArriba() {
    medir();
    const lista = articulos();
    const exceso = Math.max(0, lista.length - MAXIMO);
    for (let i = 0; i < exceso; i++) lista[i].remove();
    inicio += exceso;
    actualizarEspaciadores();
}
function recortarAbajo() {
    medir();
    const lista = articulos();
    const exceso = Math.max(0, lista.length - MAXIMO);
    for (let i = 0; i < exceso; i++) lista[lista.length - 1 - i].remove();
    fin -= exceso;
    actualizarEspaciadores();
}
async function cargarAbajo() {
    if (cargando || finalAlcanzado) return;
    cargando = true;
    try {
        const datos = await solicitar(fin);
        const desde = fin;
        datos.forEach((dato, i) => contenedor.insertBefore(crear(dato, desde + i), inferior));
        fin += datos.length;
        totalConocido = Math.max(totalConocido, fin);
        if (datos.length < TAMANO) finalAlcanzado = true;
        recortarArriba();
        actualizarEspaciadores();
    } catch (error) { console.error('Error al cargar abajo:', error); }
    finally { cargando = false; }
}
async function cargarArriba() {
    if (cargando || inicio === 0) return;
    cargando = true;
    try {
        const desde = Math.max(0, inicio - TAMANO);
        const datos = await solicitar(desde, inicio - desde);
        const referencia = articulos()[0] || inferior;
        const posicionAnterior = referencia.getBoundingClientRect().top;
        const fragmento = document.createDocumentFragment();
        datos.forEach((dato, i) => fragmento.appendChild(crear(dato, desde + i)));
        contenedor.insertBefore(fragmento, referencia);
        inicio = desde;
        recortarAbajo();
        actualizarEspaciadores();
        // Conserva el mismo artículo en la misma posición visual.
        const diferencia = referencia.getBoundingClientRect().top - posicionAnterior;
        window.scrollBy(0, diferencia);
        ultimaPosicion = window.scrollY;
    } catch (error) { console.error('Error al cargar arriba:', error); }
    finally { cargando = false; }
}
let pendiente = false;
function revisar() {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(async () => {
        pendiente = false;
        if (cargando) return;
        const actual = window.scrollY;
        const subiendo = actual < ultimaPosicion;
        ultimaPosicion = actual;
        const lista = articulos();
        if (!lista.length) return;
        const primero = lista[0].getBoundingClientRect();
        const ultimo = lista[lista.length - 1].getBoundingClientRect();
        if (subiendo && inicio > 0 && primero.top > -UMBRAL) {
            await cargarArriba();
        } else if (!subiendo && !finalAlcanzado && ultimo.bottom < window.innerHeight + UMBRAL) {
            await cargarAbajo();
        }
        // Permite llenar pantallas grandes sin exigir scroll previo.
        if (!finalAlcanzado && window.scrollY === 0 && articulos().at(-1)?.getBoundingClientRect().bottom < window.innerHeight + UMBRAL) {
            await cargarAbajo();
            if (!finalAlcanzado) revisar();
        }
    });
}
window.addEventListener('scroll', revisar, { passive: true });
window.addEventListener('resize', revisar);
(async () => { await cargarAbajo(); revisar(); })();
