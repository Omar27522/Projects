<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <script src="table_sort.js" defer></script>
    <title>Expenses</title>
</head>

<body>
    <h1>Add New Expense</h1>
    <form method="POST" action="">
    <section>
        <input type="text" name="date" placeholder="Date"
            value="<?php date_default_timezone_set("America/Los_Angeles"); echo date("M-j"); ?>" required>
        <br/ ><input type="text" name="item" placeholder="Item" required>
        <br/ ><input type="text" name="place" placeholder="Place" required>
        <br/ ><input type="number" step="1" name="amount" placeholder="Amount" min="0" required>
        <br/ ><select name="type" required>
            <option value="">Type</option>
            <option value="misc">Misc</option>
            <option value="food">Food</option>
            <option value="entertainment">Entertainment</option>
            <option value="tithe">Tithe</option>
            <option value="repairs">Repairs</option>
            <option value="maintenance">Maintenance</option>
            <option value="clothing">Clothing</option>
            <option value="gifts">Gifts</option>
            <option value="personal">Personal</option>
            <option value="tax">Tax</option>
        </select>
        </section>
        <input type="submit" value="Add Expense">
    </form>
    <?php
    require_once 'db_connect.php';
    $db = new Database();
    $expenses = $db->getAllExpenses();

    
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Add current time to the date
        $submittedDate = $_POST['date'];
        $currentTime = date("g:i A");
        $dateWithTime = $submittedDate . " " . $currentTime;
        
        $result = $db->addExpense(
            $dateWithTime,
            $_POST['item'],
            $_POST['place'],
            $_POST['amount'],
            $_POST['type']
        );
        
        if ($result) {
            echo "<p style='color: green;'>Expense added successfully!</p>";
        } else {
            echo "<p style='color: red;'>Error adding expense.</p>";
        }
    }
    ?>

<div class="footer">
 <a href="monthly.php">Monthly Expenses</a>
 <a href="#GAS">GAS</a>
 <a href="#Budget">Budget</a>
 <a href="#tips">tips</a>
 <a href="#LAPC">LAPC</a>
 <a href="#Bank">Bank</a>
<div>
</body>

</html>