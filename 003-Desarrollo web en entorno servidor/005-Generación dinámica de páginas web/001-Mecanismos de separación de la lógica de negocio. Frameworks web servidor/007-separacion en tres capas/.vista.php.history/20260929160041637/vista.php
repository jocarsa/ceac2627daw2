<?php
	class JocarsaVista{
  
  	constructor(){
    	$json
    }
    function pintaTabla($this->json){
        $datos = json_decode($json, true);
        if (!$datos || count($datos) == 0) {
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
                echo "<td>" . htmlspecialchars($valor) . "</td>";
            }
            echo "</tr>";
        }
        echo "</tbody>";
        echo "</table>";
    }

    function pintaFormulario($this->json){

    }
  }
?>