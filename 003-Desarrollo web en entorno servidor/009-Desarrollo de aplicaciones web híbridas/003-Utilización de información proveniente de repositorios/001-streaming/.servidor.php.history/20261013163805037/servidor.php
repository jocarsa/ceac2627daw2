
<?php
// Leer archivo JSON
$json = file_get_contents("repositorio/titulos.json");

// Convertir JSON a array PHP
$datos = json_decode($json, true);

// Obtener las 10 primeras películas
$peliculas = array_slice($datos["peliculas"], 0, 10);

// Mostrar resultados
foreach ($peliculas as $pelicula) {
    echo "<h2>" . htmlspecialchars($pelicula["titulo"]) . "</h2>";
    echo "<p>Género: " . htmlspecialchars($pelicula["genero"]) . "</p>";
    echo "<p>Año: " . $pelicula["anio"] . "</p>";
    echo "<img src='portadas/" . htmlspecialchars($pelicula["imagen"]) . "' width='150'>";
    echo "<hr>";
}
?>
