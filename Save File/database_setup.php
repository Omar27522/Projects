<?php
// Define the path to the database file
$db_file = 'saveFile.sqlite';

if (!file_exists($db_file)) {
    // Create the database file
    $pdo = new PDO('sqlite:' . $db_file);

    // Create a table (modify as per your needs)
    $sql = "
        CREATE TABLE IF NOT EXISTS your_table (
            id INTEGER PRIMARY KEY,
            title TEXT,
            data TEXT
        );
    ";
    $pdo->exec($sql);

    echo "Database and table created successfully.";
} else {
    // Check if the table exists
    $pdo = new PDO('sqlite:' . $db_file);
    $result = $pdo->query("SELECT name FROM sqlite_master WHERE type='table' AND name='your_table'");
    if ($result && $result->fetch()) {
        //echo "Table 'your_table' already exists.";
    } else {
        // Create the table if it does not exist
        $sql = "
            CREATE TABLE your_table (
                id INTEGER PRIMARY KEY,
                title TEXT,
                data TEXT
            );
        ";
        $pdo->exec($sql);
        echo "Table 'your_table' created successfully.";
    }
}
?>
