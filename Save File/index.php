<?php
    // Ensure the database is set up
    include 'database_setup.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Tables</title>
</head>
<body>
    <h1>Edit Data</h1>

    <form id="editableTableForm" method="post" action="saveTable.php">
        <table id="editableTable">
            <!-- Table headers -->
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Age</th>
                    <!-- Add more headers as needed -->
                </tr>
            </thead>
            <!-- Table body with data -->
            <tbody>
                <tr>
                    <td><input type="text" name="id[]" value=" <?php echo $row['id']; ?>"></td>
                    <td><input type="text" name="name[]" value=""></td>
                    <td><input type="text" name="age[]" value=""></td>
                    <!-- Add more data rows as needed -->
                </tr>
                <!-- Data From the Database -->
                <?php
                    $pdo = new PDO('sqlite:saveFile.sqlite');
                    $result = $pdo->query("SELECT * FROM your_table");
                    while ($row = $result->fetch()) {
                        echo '<tr>';
                        echo '<td><input type="text" name="id[]" value="' . $row['id'] . '"></td>';
                        echo '<td><input type="text" name="name[]" value="' . $row['name'] . '"></td>';
                        echo '<td><input type="text" name="age[]" value="' . $row['age'] . '"></td>';
                        echo '</tr>';
                    }
                ?>
            </tbody>
        </table>
        <button type="submit">Save Changes</button>
    </form>
</body>
</html>