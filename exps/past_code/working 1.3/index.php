<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Expenses</title>
</head>

<body>
    <h1>Add New Expense</h1>
    <form method="POST" action="">
        <input type="text" name="date" placeholder="Date"
            value="<?php date_default_timezone_set("America/Los_Angeles"); echo date("M-j"); ?>" required>
        <input type="text" name="item" placeholder="Item" required>
        <input type="text" name="place" placeholder="Place" required>
        <input type="number" step="1" name="amount" placeholder="Amount" required>
        <select name="type" required>
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
        <input type="submit" value="Add Expense">
    </form>
    <?php
    require_once 'db_connect.php';
    $db = new Database();
    $expenses = $db->getAllExpenses();
    
    if (!empty($expenses)) {
        echo "<hr>";
        echo "<a href='expenses.php'>View All Expenses</a>";
    }
    
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

<details style="padding-top: 100px">
    <summary>Other button</summary>
    More other things for this button
</details>


</body>

</html>