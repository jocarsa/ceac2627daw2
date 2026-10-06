<?php
	class JocarsaModelo{
  
  	public function __construct($basededatos) {
        $this->bd = new PDO('sqlite:'+$basededatos);
        
    }
  	dameDatos($tabla){
      $info = $this->bd->query("SELECT * FROM ".$tabla);
      return $info->fetchAll(PDO::FETCH_ASSOC);
    }

    insertaDatos($tabla,$datos){
      $info = $this->bd->query("INSERT INTO ".$tabla." VALUES(".$datos.")");
      return 0;
    }

    eliminaDatos($tabla,$id){
      $info = $this->bd->query("DELETE FROM ".$tabla." WHERE id = ".$id."");
      return 0;
    }
  }
?>