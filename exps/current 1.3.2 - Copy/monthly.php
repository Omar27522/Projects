<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <script src="table_sort.js" defer></script>
    <title>Monthly Expenses</title>
</head>

<body>

    <h1>Monthly Expenses</h1><a href="index.php">Back</a>
    <div class="monthly-summary">
        <?php
        require_once 'db_connect.php';
        $db = new Database();       
        $total = 0;
        
        // Calculate total first
        $rows = [];
        $currentMonth = date('m');
        $selectedMonth = isset($_GET['month']) ? $_GET['month'] : $currentMonth;
        $currentYear = date('Y');
        
        $monthlyExpenses = $db->getExpensesByMonthYear($selectedMonth, $currentYear);
        
        while ($row = $monthlyExpenses->fetchArray(SQLITE3_ASSOC)) {
            $total += $row['amount'];
            $rows[] = $row;
        }
        
        // Display total
        $months = [
            '01' => 'January', '02' => 'February', '03' => 'March',
            '04' => 'April', '05' => 'May', '06' => 'June',
            '07' => 'July', '08' => 'August', '09' => 'September',
            '10' => 'October', '11' => 'November', '12' => 'December'
        ];

        echo "<div style='margin-bottom: 15px;'>Monthly Total: <strong>$" . number_format($total) . "|</strong>
        <select id='monthSelect' style=\"display:inline-block; width: 170px; margin-left:4px;\" name=\"month\">";
        foreach ($months as $num => $name) {
            $selected = ($num == $selectedMonth) ? 'selected' : '';
            echo "<option value='$num' $selected>$name</option>";
        }
    echo "</select><a href=\"download_data.php\" style=\"margin-right:14px;float:right;\">DOWNLOAD DATA</a></div>";

        echo "<h3>" . $months[$selectedMonth] . " " . $currentYear . " Expenses</h3>";
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

        // Display rows h:i:a this is the HOur and minutes in 12 hour format
        foreach ($rows as $row) {
            echo "<tr>";
            echo "<td>" . date('M-j', strtotime($row['date'])) . "</td>";
            echo "<td>" . htmlspecialchars($row['item']) . "</td>";
            echo "<td>" . htmlspecialchars($row['place']) . "</td>";
            echo "<td>" . ucfirst($row['type']) . "</td>";
            echo "<td>$" . number_format($row['amount']) . "</td>";
            echo "</tr>";
        }
        echo "<tr class='total-row'>";
        echo "<td colspan='5'><strong>Total $" . number_format($total) . "</strong></td>";
        
        echo "</tr>";
        echo "</tbody>";
        echo "</table>";
        ?>
        <script>
        document.getElementById('monthSelect').addEventListener('change', function() {
            const month = this.value;
            window.location.href = `monthly.php?month=${month}`;
        });
        </script>
    </div>
</body>

</html>