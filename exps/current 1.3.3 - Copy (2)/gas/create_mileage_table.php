<?php
require_once '../db_connect.php';

try {
    $db = new Database();
    
    // Create mileage_tracking table
    $sql = "CREATE TABLE IF NOT EXISTS mileage_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month VARCHAR(7),
        first_miles DECIMAL(10,1),
        last_miles DECIMAL(10,1),
        monthly_total DECIMAL(10,1),
        cumulative_total DECIMAL(10,1),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )";

    $db->exec($sql);
    echo "Mileage tracking table created successfully";
} catch(PDOException $e) {
    echo "Error creating table: " . $e->getMessage();
}
?>
