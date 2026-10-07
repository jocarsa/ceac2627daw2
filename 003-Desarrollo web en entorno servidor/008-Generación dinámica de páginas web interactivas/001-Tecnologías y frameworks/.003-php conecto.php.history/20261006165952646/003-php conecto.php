<?php

// Connect to SQLite database
$db = new PDO("sqlite:database.db");

// Show errors as exceptions
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

echo "Connected to SQLite";

?>