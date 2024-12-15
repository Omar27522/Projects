<!DOCTYPE html>
<?php       include '../db_connect.php';  ?>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../style.css">
    <script src="../table_sort.js" defer></script>
    <title>Monthly Expenses</title>
</head>
<style>
    .back-button{
        text-decoration: none;
        color: black;
        font-size:larger;
        border: 1px solid black;
        padding: 5px 10px;
        margin-left: 10px;
        border-radius: 5px;
        transition: background-color 0.3s ease;
        display: inline;
        width: fit-content;
    }
    .back-button:hover{
        background-color: #e0e0e0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .back-button:active{
        background-color: #c0c0c0;
        transform: scale(0.98);
        transition: transform 0.2s ease;
    }

    .download-data{
        margin-right:14px;float:right;
        background-color: #f2f2f2;
        border: 1px solid #ccc;
        padding: 8px 16px;
        border-radius: 4px;
        text-decoration: none;
        color: #333;
        font-size: 14px;
        transition: background-color 0.3s ease;
    }
    .download-data:hover{
        background-color: #e0e0e0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transform: scale(0.98);
        transition: transform 0.2s ease;
    }
    .download-data:active{
        background-color: #c0c0c0;
        transform: scale(0.96);
        transition: transform 0.2s ease;
    }
</style>
<body>
<h1 style="float: left; display: inline;">Monthly Expenses</h1>
    <a href="../" class="back-button">Back</a>
    <?php
    try {
        $db = new Database();
        $total = 0;

        // Calculate total first
        $rows = [];
        $currentMonth = date('m');
        $selectedMonth = isset($_GET['month']) ? $_GET['month'] : $currentMonth;
        $currentYear = date('Y');

        $expenses = $db->getAllExpenses();
        if ($expenses === null) {
            echo "<p style='color: red;'>Error: Could not fetch expenses</p>";
        }

        // Filter expenses for selected month
        $monthlyExpenses = array_filter($expenses, function($expense) use ($selectedMonth, $currentYear) {
            return date('m', strtotime($expense['date'])) == $selectedMonth &&
                   date('Y', strtotime($expense['date'])) == $currentYear;
        });

        foreach ($monthlyExpenses as $expense) {
            $total += $expense['amount'];
        }

        // Display month selector
        $months = [
            '01' => 'January', '02' => 'February', '03' => 'March',
            '04' => 'April', '05' => 'May', '06' => 'June',
            '07' => 'July', '08' => 'August', '09' => 'September',
            '10' => 'October', '11' => 'November', '12' => 'December'
        ];

        echo "<div style='margin-bottom: 15px;'>Monthly Total: <strong>$" . number_format($total) . "</strong>
        <select id='monthSelect' style=\"display:inline-block; width: 170px; margin-left:4px;\" name=\"month\">";
        foreach ($months as $num => $name) {
            $selected = ($num == $selectedMonth) ? 'selected' : '';
            echo "<option value='$num' $selected>$name</option>";
        }
        echo "</select><a href=\"download_data.php\" class=\"download-data\">DOWNLOAD DATA</a></div>";

        echo "<h3>" . $months[$selectedMonth] . " " . $currentYear . " Expenses</h3>";
        echo '<table class="sortable">';
        echo '<thead>';
        echo '<tr>';
        echo '<th>Date</th>';
        echo '<th>Item</th>';
        echo '<th>Place</th>';
        echo '<th>Amount</th>';
        echo '<th>Type</th>';
        echo '</tr>';
        echo '</thead>';
        echo '<tbody>';

        foreach ($monthlyExpenses as $expense) {
            echo '<tr>';
            echo '<td>' . date('M-j', strtotime($expense['date'])) . '</td>';
            echo '<td>' . htmlspecialchars($expense['item']) . '</td>';
            echo '<td>' . htmlspecialchars($expense['place']) . '</td>';
            echo '<td>$' . number_format($expense['amount']) . '</td>';
            echo '<td>' . htmlspecialchars($expense['type']) . '</td>';
            echo '</tr>';
        }
        echo '</tbody>';
        echo '</table>';
    } catch (Exception $e) {
        echo "<p style='color: red;'>Error: " . $e->getMessage() . "</p>";
    }
    ?>
    <script>
    document.getElementById('monthSelect').addEventListener('change', function() {
        const month = this.value;
        window.location.href = `?month=${month}`;
    });
    </script>
    <?php
    footer();
    ?>
</body>
</html>