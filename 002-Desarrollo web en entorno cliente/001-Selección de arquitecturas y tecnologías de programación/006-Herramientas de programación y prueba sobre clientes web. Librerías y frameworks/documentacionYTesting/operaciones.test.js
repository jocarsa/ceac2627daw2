const {
    sumar,
    restar,
    calcularPrecio
} = require("./operaciones");


test("2 + 3 debe ser 5", function () {

    expect(sumar(2, 3)).toBe(5);

});


test("10 - 4 debe ser 6", function () {

    expect(restar(10, 4)).toBe(6);

});


test("100 € con 20 € de descuento debe dar 80 €", function () {

    expect(calcularPrecio(100, 20)).toBe(80);

});


test("50 € sin descuento debe dar 50 €", function () {

    expect(calcularPrecio(50, 0)).toBe(50);

});