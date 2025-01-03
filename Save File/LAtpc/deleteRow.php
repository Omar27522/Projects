<?php
require_once 'database_setup.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['id'])) {
    try {
        $stmt = $pdo->prepare("DELETE FROM your_table WHERE id = ?");
        $stmt->execute([$_POST['id']]);
        echo "success";
    } catch (Exception $e) {
        http_response_code(500);
        echo "Error: " . $e->getMessage();
    }
}
?>
