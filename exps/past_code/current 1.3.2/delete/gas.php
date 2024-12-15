<!DOCTYPE html>
<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $date = $_POST['date'] ?? '';
    $station = $_POST['station'] ?? '';
    $type = $_POST['type'] ?? '';
    $amount = $_POST['amount'] ?? '';
    $gallons = $_POST['gallons'] ?? '';
    $price = $_POST['price'] ?? '';
    
    // You might want to add validation here
    
    // For now, we'll use JavaScript to add the row dynamically
}
?>
<html lang="en">
<head>
<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <script src="table_sort.js" defer></script>
    <title>GAS</title>
</head>
<body>
<h1>GAS</h1>
<h2>Month: current month</h2>


<table>
<tr>
        <th>date</th>
        <th>station</th>
        <th>type</th>
        <th>Amount</th>
        <th>Gallons</th>
        <th>Actual Price per gallon</th>
    </tr>
    <tr>
        <td>12/9</td>
        <td>Pemex</td>
        <td>Pre</td>
        <td>67.69</td>
        <td>16.948</td>
        <td>3.99</td>
    </tr>

</table>

<!-- Add new entry form -->
<div class="input-form">
    <h3>Add New Gas Entry</h3>
    <form id="gasForm" method="post" onsubmit="return addNewRow(event)">
        <div class="form-group">
            <label for="date">Date:</label>
            <input type="text" id="date" name="date" required>
        </div>
        <div class="form-group">
            <label for="station">Station:</label>
            <input type="text" id="station" name="station" required>
        </div>
        <div class="form-group">
            <label for="type">Type:</label>
            <input type="text" id="type" name="type" required>
        </div>
        <div class="form-group">
            <label for="amount">Amount:</label>
            <input type="number" id="amount" name="amount" step="0.01" required>
        </div>
        <div class="form-group">
            <label for="gallons">Gallons:</label>
            <input type="number" id="gallons" name="gallons" step="0.001" required>
        </div>
        <div class="form-group">
            <label for="price">Price per gallon:</label>
            <input type="number" id="price" name="price" step="0.01" required>
        </div>
        <button type="submit">Add Entry</button>
    </form>
</div>

<script>
function addNewRow(event) {
    event.preventDefault();
    
    const table = document.querySelector('table');
    const newRow = document.createElement('tr');
    
    const fields = ['date', 'station', 'type', 'amount', 'gallons', 'price'];
    fields.forEach(field => {
        const td = document.createElement('td');
        td.textContent = document.getElementById(field).value;
        newRow.appendChild(td);
    });
    
    table.appendChild(newRow);
    document.getElementById('gasForm').reset();
    return false;
}
</script>

<style>
.input-form {
    margin: 20px 0;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

.form-group {
    margin-bottom: 10px;
}

.form-group label {
    display: inline-block;
    width: 120px;
    margin-right: 10px;
}

.form-group input {
    padding: 5px;
    border: 1px solid #ccc;
    border-radius: 3px;
}

button {
    margin-top: 10px;
    padding: 8px 15px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}

button:hover {
    background-color: #45a049;
}
</style>
</body>
</html>