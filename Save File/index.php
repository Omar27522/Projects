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
                    <th>Title</th>
                    <th>Data</th>
                    <th>Edit</th>
                    <!-- Add more headers as needed -->
                </tr>
            </thead>
            <!-- Table body with data -->
            <tbody>
                <tr>
                    <td><input type="hidden" name="id[]" value=""></td>
                    <td><input type="text" name="title[]" value=""></td>
                    <td><input type="text" name="data[]" value=""></td>
                    <td></td>
                    <!-- Add more data rows as needed -->
                </tr>
                <!-- Data From the Database -->
                <?php
                    $pdo = new PDO('sqlite:saveFile.sqlite');
                    $result = $pdo->query("SELECT * FROM your_table");
                    while ($row = $result->fetch()) {
                        echo '<tr>';
                        echo '<td><input type="text" name="id[]" value="' . $row['id'] . '"></td>';
                        echo '<td><input type="text" name="title[]" value="' . $row['title'] . '"></td>';
                        echo '<td><input type="text" name="data[]" value="' . $row['data'] . '"></td>';
                        echo '<td><button type="button" class="delete-button">Delete</button></td>';
                        echo '</tr>';
                    }
                ?>
            </tbody>
        </table>
        <button type="submit">Save Changes</button>
    </form>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const deleteButtons = document.querySelectorAll('.delete-button');
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const row = this.closest('tr');
                const id = row.querySelector('input[name="id[]"]').value;
                
                if (confirm('Are you sure you want to delete this row?')) {
                    fetch('deleteRow.php', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: 'id=' + encodeURIComponent(id)
                    })
                    .then(response => response.text())
                    .then(result => {
                        if (result === 'success') {
                            row.remove();
                        } else {
                            alert('Error deleting row: ' + result);
                        }
                    })
                    .catch(error => {
                        alert('Error: ' + error);
                    });
                }
            });
        });
    });
    </script>
</body>
</html>