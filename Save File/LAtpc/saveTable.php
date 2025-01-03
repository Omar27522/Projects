<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    try {
        require_once 'database_setup.php';
        $pdo->beginTransaction();

        for ($i = 0; $i < count($_POST['id']); $i++) {
            // Skip if both title and data are empty
            if (empty($_POST['title'][$i]) && empty($_POST['data'][$i])) {
                continue;
            }

            if (empty($_POST['id'][$i])) {
                // Insert new record
                $stmt = $pdo->prepare("INSERT INTO your_table (title, data) VALUES (?, ?)");
                $stmt->execute([$_POST['title'][$i], $_POST['data'][$i]]);
            } else {
                // Update existing record
                $stmt = $pdo->prepare("UPDATE your_table SET title = ?, data = ? WHERE id = ?");
                $stmt->execute([$_POST['title'][$i], $_POST['data'][$i], $_POST['id'][$i]]);
            }
        }
        $pdo->commit();
        header("Location: index.php");
    } catch (Exception $e) {
        $pdo->rollBack();
        echo "Error: " . $e->getMessage();
    }
}
?>
