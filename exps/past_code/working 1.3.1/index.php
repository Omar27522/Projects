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

<details id="monthlyExpenses">
    <summary>Monthly Expenses</summary>
    <div class="monthly-summary">
        <?php
        require_once 'db_connect.php';
        $db = new Database();       
        $monthlyExpenses = $db->getMonthlyExpenses();
        $total = 0;
        
        // Calculate total first
        $rows = [];
        while ($row = $monthlyExpenses->fetchArray(SQLITE3_ASSOC)) {
            $total += $row['amount'];
            $rows[] = $row;
        }
        
        // Display total
        echo "<div style='margin-bottom: 15px;'>Monthly Total: <strong>$" . number_format($total, 2) . "</strong>
        <select style=\"display:inline-block; width: 170px; margin-left:4px;\" name=\"month\"><option>Choose Month</option><option>January</option></select>
        
        </div>";
        echo "<h3>" . date('F Y') . " Expenses</h3>";
        echo "<table class='monthly-table'>";
        echo "<thead>";
        echo "<tr>
            <th onclick='sortTable(0)' data-sort='asc'>Date</th>
            <th onclick='sortTable(1)' data-sort='asc'>Item</th>
            <th onclick='sortTable(2)' data-sort='asc'>Place</th>
            <th onclick='sortTable(3)' data-sort='asc'>Type</th>
            <th onclick='sortTable(4)' data-sort='asc'>Amount</th>
        </tr>";
        echo "</thead>";
        echo "<tbody>";
        
        // Display rows
        foreach ($rows as $row) {
            echo "<tr>";
            echo "<td>" . date('M-j h:i:a', strtotime($row['date'])) . "</td>";
            echo "<td>" . htmlspecialchars($row['item']) . "</td>";
            echo "<td>" . htmlspecialchars($row['place']) . "</td>";
            echo "<td>" . ucfirst($row['type']) . "</td>";
            echo "<td>$" . number_format($row['amount'], 2) . "</td>";
            echo "</tr>";
        }
        echo "<tr class='total-row'>";
        echo "<td colspan='4'><strong>Total</strong></td>";
        echo "<td><strong>$" . number_format($total, 2) . "</strong></td>";
        echo "</tr>";
        echo "</tbody>";
        echo "</table>";
        ?>
    </div>
</details>

 
</body>

</html>