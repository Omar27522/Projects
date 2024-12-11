<!DOCTYPE html>
<?php
require_once 'db_connect.php';
$db = new Database();

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['add_station'])) {
        $new_station = $_POST['new_station'] ?? '';
        if (!empty($new_station)) {
            $db->addStation($new_station);
        }
        header("Location: " . $_SERVER['PHP_SELF']);
        exit();
    }
    
    $date = $_POST['date'] ?? '';
    $station = $_POST['station'] ?? '';
    $type = $_POST['type'] ?? '';
    $amount = $_POST['amount'] ?? '';
    $gallons = $_POST['gallons'] ?? '';
    $price = $_POST['price'] ?? '';
    
    try {
        $db->addGasEntry($date, $station, $type, $amount, $gallons, $price);
        header("Location: " . $_SERVER['PHP_SELF']);
        exit();
    } catch(Exception $e) {
        echo "Error: " . $e->getMessage();
    }
}

// Fetch all gas entries
$entries = [];
try {
    $result = $db->getAllGasEntries();
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $entries[] = $row;
    }
} catch(Exception $e) {
    echo "Error: " . $e->getMessage();
}

// Fetch all stations
$stations = [];
try {
    $result = $db->getAllStations();
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $stations[] = $row;
    }
} catch(Exception $e) {
    echo "Error: " . $e->getMessage();
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

<!-- Add new entry form -->
<div class="boxes-container">
    <div class="left-column">
        <div class="box">
            <h3>Add New Gas Entry</h3>
            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                <div class="form-group">
                    <label for="date">Date:</label>
                    <input type="date" id="date" name="date" value="<?php echo date('Y-m-d'); ?>" required>
                </div>
                <div class="form-group">
                    <label for="station">Station:</label>
                    <select id="station" name="station" required>
                        <option value="">Select Station</option>
                        <?php foreach ($stations as $station) { ?>
                        <option value="<?php echo $station['name']; ?>"><?php echo $station['name']; ?></option>
                        <?php } ?>
                    </select>
                </div>
                <div class="form-group">
                    <label for="type">Type:</label>
                    <div class="select-wrapper">
                        <select id="type" name="type" required>
                            <option value="">Select Type</option>
                            <option value="Regular">Regular</option>
                            <option value="Plus">Plus</option>
                            <option value="Premium">Premium</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="amount">Amount:</label>
                    <div class="input-with-symbol">
                        <span class="currency-symbol">$</span>
                        <input type="number" id="amount" name="amount" step="0.01" required>
                    </div>
                </div>
                <div class="form-group">
                    <label for="gallons">Gallons:</label>
                    <div class="input-with-symbol">
                        <span class="unit-symbol">gal</span>
                        <input type="number" id="gallons" name="gallons" step="0.001" required>
                    </div>
                </div>
                <div class="form-group">
                    <label for="price">Price/Gallon:</label>
                    <div class="input-with-symbol">
                        <span class="currency-symbol">$</span>
                        <input type="number" id="price" name="price" step="0.01" required>
                    </div>
                </div>
                <button type="submit">Add Entry</button>
            </form>
        </div>
    </div>
    <div class="right-column">
        <div class="box">
            <h3>Add New Station</h3>
            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                <div class="form-group">
                    <label for="new_station">Station Name:</label>
                    <input type="text" id="new_station" name="new_station" required>
                </div>
                <button type="submit" name="add_station">Add Station</button>
            </form>
        </div>
        <div class="box">
            <h3>Price Calculator</h3>
            <div class="form-group">
                <label for="calc_amount">Amount:</label>
                <div class="input-with-symbol">
                    <span class="currency-symbol">$</span>
                    <input type="number" id="calc_amount" step="0.01" oninput="calculatePrice()">
                </div>
            </div>
            <div class="form-group">
                <label for="calc_gallons">Gallons:</label>
                <input type="number" id="calc_gallons" step="0.001" oninput="calculatePrice()">
            </div>
            <div class="form-group">
                <label for="calc_price">Price/Gallon:</label>
                <div class="input-with-symbol">
                    <span class="currency-symbol">$</span>
                    <input type="number" id="calc_price" readonly>
                </div>
            </div>
        </div>
    </div>
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

function calculatePrice() {
    const amount = parseFloat(document.getElementById('calc_amount').value);
    const gallons = parseFloat(document.getElementById('calc_gallons').value);
    const price = amount / gallons;
    document.getElementById('calc_price').value = price.toFixed(2);
}
</script>

<style>
.input-form {
    margin: 20px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

/* Add spacing between forms */
.input-form + .input-form {
    margin-top: 10px;
}

/* Make the new station form more compact */
.input-form:nth-child(2) {
    max-width: 300px;
}

input#new_station {
    width: 200px;
}

.form-group {
    margin: 15px 0;
    display: flex;
    align-items: center;
}

.form-group label {
    width: 100px;
    margin-right: 15px;
}

/* Base style for all inputs */
input[type="text"],
input[type="number"],
input[type="date"],
.select-wrapper select {
    width: 200px;
    padding: 10px;
    padding-right: 30px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
    font-size: 14px;
    height: 38px;
}

/* Focus state for all inputs */
input:focus,
.select-wrapper select:focus {
    outline: none;
    border-color: #2e8b57;
    color: #2e8b57;
}

/* Amount input specific styles */
.input-with-symbol {
    position: relative;
    display: inline-block;
}

.currency-symbol {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 14px;
    color: #666;
}

.unit-symbol {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 14px;
    color: #666;
}

.input-with-symbol input[type="number"] {
    padding-left: 25px;
}

/* Remove spinner buttons from number inputs */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

input[type="number"] {
    -moz-appearance: textfield;
}

.select-wrapper {
    position: relative;
    display: inline-block;
}

.select-wrapper::after {
    content: "";
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #666;
    pointer-events: none;
}

.select-wrapper select {
    padding-right: 30px;
    background-color: white;
    cursor: pointer;
}

.select-wrapper select:focus {
    outline: none;
    border-color: #2e8b57;
    color: #2e8b57;
}

.select-wrapper select:focus + .select-wrapper::after {
    border-top-color: #2e8b57;
}

button {
    margin-top: 10px;
    padding: 8px 15px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    width:200px
}

button:hover {
    background-color: #45a049;
}

.boxes-container {
    display: flex;
    gap: 20px;
    margin: 20px;
}

.left-column {
    flex: 1;
    min-width: 400px;
}

.right-column {
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 350px;
}

.box {
    padding: 20px;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.box h3 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #333;
    font-size: 18px;
    text-align: center;
}

@media (max-width: 1000px) {
    .boxes-container {
        flex-direction: column;
    }
    
    .right-column {
        width: 100%;
    }
    
    .left-column {
        min-width: 100%;
    }
}

/* Calculator specific styles */
#calc_price {
    background-color: #f8f8f8;
    color: #2e8b57;
    font-weight: bold;
}

/* Box specific styles */
.box:nth-child(1) {
    flex: 2;
}

.box:nth-child(2), .box:nth-child(3) {
    flex: 1;
}

@media (max-width: 1200px) {
    .box {
        flex: 1 1 100%;
    }
}
</style>
<table>
<tr>
        <th>date</th>
        <th>station</th>
        <th>type</th>
        <th>Amount</th>
        <th>Gallons</th>
        <th>Actual Price per gallon</th>
    </tr>
    <?php foreach ($entries as $entry) { ?>
    <tr>
        <td><?php echo $entry['date']; ?></td>
        <td><?php echo $entry['station']; ?></td>
        <td><?php echo $entry['type']; ?></td>
        <td><?php echo $entry['amount']; ?></td>
        <td><?php echo $entry['gallons']; ?></td>
        <td><?php echo $entry['price']; ?></td>
    </tr>
    <?php } ?>
</table>
</body>
</html>