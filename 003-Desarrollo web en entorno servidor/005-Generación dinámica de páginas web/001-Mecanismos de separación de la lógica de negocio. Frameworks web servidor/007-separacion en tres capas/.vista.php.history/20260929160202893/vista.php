<?php

class JocarsaVista {

    private $json;
    private $datos;

    // Constructor
    public function __construct($json) {
        $this->json = $json;
        $this->datos = json_decode($json, true);

        if (!is_array($this->datos)) {
            $this->datos = [];
        }
    }


    // ==============================
    // PINTAR TABLA
    // ==============================

    public function pintaTabla() {

        $datos = $this->datos;

        if (count($datos) == 0) {
            echo "<p>No hay datos</p>";
            return;
        }

        echo "<table border='1'>";

        // Cabeceras
        echo "<thead>";
        echo "<tr>";

        foreach ($datos[0] as $clave => $valor) {
            echo "<th>" . htmlspecialchars($clave) . "</th>";
        }

        echo "</tr>";
        echo "</thead>";


        // Datos
        echo "<tbody>";

        foreach ($datos as $fila) {

            echo "<tr>";

            foreach ($fila as $valor) {
                echo "<td>" . htmlspecialchars((string)$valor) . "</td>";
            }

            echo "</tr>";
        }

        echo "</tbody>";

        echo "</table>";
    }


    // ==============================
    // PINTAR FORMULARIO
    // ==============================

    public function pintaFormulario($action = "", $method = "POST") {

        $datos = $this->datos;

        if (count($datos) == 0) {
            echo "<p>No hay estructura para generar el formulario</p>";
            return;
        }

        // Tomamos la primera fila como modelo
        $modelo = $datos[0];

        echo "<form action='" . htmlspecialchars($action) . "' ";
        echo "method='" . htmlspecialchars($method) . "'>";

        foreach ($modelo as $campo => $valor) {

            echo "<div>";

            echo "<label for='" . htmlspecialchars($campo) . "'>";
            echo htmlspecialchars(ucfirst($campo));
            echo "</label>";

            echo "<br>";

            echo "<input 
                    type='text'
                    id='" . htmlspecialchars($campo) . "'
                    name='" . htmlspecialchars($campo) . "'
                    value=''
                  >";

            echo "</div>";

            echo "<br>";
        }

        echo "<input type='submit' value='Enviar'>";

        echo "</form>";
    }

}
?>