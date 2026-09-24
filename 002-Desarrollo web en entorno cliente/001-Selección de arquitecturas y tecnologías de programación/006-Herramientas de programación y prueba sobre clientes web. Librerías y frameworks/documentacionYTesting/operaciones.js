/**
 * Suma dos números.
 *
 * @param {number} a Primer número.
 * @param {number} b Segundo número.
 * @returns {number} Resultado de la suma.
 */
function sumar(a, b) {
    return a + b;
}


/**
 * Resta dos números.
 *
 * @param {number} a Primer número.
 * @param {number} b Segundo número.
 * @returns {number} Resultado de la resta.
 */
function restar(a, b) {
    return a - b;
}


/**
 * Calcula el precio final de un producto
 * después de aplicar un descuento.
 *
 * @param {number} precio Precio original del producto.
 * @param {number} descuento Cantidad que se debe descontar.
 * @returns {number} Precio final del producto.
 */
function calcularPrecio(precio, descuento) {
    return precio - descuento;
}


/*
 * Si estamos ejecutando el archivo con Node/Jest,
 * exportamos las funciones.
 *
 * En el navegador "module" no existe,
 * así que este bloque simplemente se ignora.
 */
if (typeof module !== "undefined" && module.exports) {

    module.exports = {
        sumar,
        restar,
        calcularPrecio
    };

}