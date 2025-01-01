<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    try {
        $pdo = new PDO('sqlite:saveFile.sqlite');
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        for ($i = 0; $i < count($_POST['id']); $i++) {
            if (empty($_POST['id'][$i])) {
                // Insert new record
                $stmt = $pdo->prepare("INSERT INTO your_table (name, age) VALUES (?, ?)");
                $stmt->execute([$_POST['name'][$i], $_POST['age'][$i]]);
            } else {
                // Update existing record
                $stmt = $pdo->prepare("UPDATE your_table SET name = ?, age = ? WHERE id = ?");
                $stmt->execute([$_POST['name'][$i], $_POST['age'][$i], $_POST['id'][$i]]);
            }
        }
        header("Location: index.php");
    } catch (PDOException $e) {
        echo "Error: " . $e->getMessage();
    }
}
?>
