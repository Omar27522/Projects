<?php
require_once 'db_connect.php';

// Set timezone
date_default_timezone_set("America/Los_Angeles");
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <style>
        .filter-container {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        .filter-container select {
            padding: 2px;
        }
        .filter-container form {
            margin: 0;
        }
    </style>
    <title>Monthly Expenses</title>
</head>
<body>
    <div>
        <h1>Monthly Summary</h1>
        <a href="expenses.php">Back to Expenses</a>
    </div>
    <section>
        <div class="filter-container">
            <form method="GET" action="" style="padding: 0;width: 15%;">
                <select name="month" onchange="this.form.submit()">
                    <?php
                    $months = array(
                        1 => 'January', 2 => 'February', 3 => 'March',
                        4 => 'April', 5 => 'May', 6 => 'June',
                        7 => 'July', 8 => 'August', 9 => 'September',
                        10 => 'October', 11 => 'November', 12 => 'December'
                    );
                    $currentMonth = isset($_GET['month']) ? (int)$_GET['month'] : (int)date('n');
                    foreach ($months as $num => $name) {
                        $selected = ($num === $currentMonth) ? 'selected' : '';
                        echo "<option value='$num' $selected>$name</option>";
                    }
                    ?>
                </select>
            </form>

            <form method="GET" action="" style="padding: 0;width: 15%;">
                <input type="hidden" name="month" value="<?php echo $currentMonth; ?>">
                <select name="type" onchange="this.form.submit()">
                    <option value="">All Types</option>
                    <?php
                    $db = new Database();
                    $types = $db->getDistinctTypes();
                    $currentType = isset($_GET['type']) ? $_GET['type'] : '';
                    foreach ($types as $type) {
                        $selected = ($type === $currentType) ? 'selected' : '';
                        echo "<option value='" . htmlspecialchars($type) . "' $selected>" . htmlspecialchars($type) . "</option>";
                    }
                    ?>
                </select>
            </form>
        </div>
        <?php
        require_once 'db_connect.php';
        $db = new Database();

        // Handle delete action
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['delete_id'])) {
            $deleted = $db->deleteExpense($_POST['delete_id']);
            if ($deleted) {
                echo "<p style='color: green;'>Expense deleted successfully!</p>";
            } else {
                echo "<p style='color: red;'>Error deleting expense.</p>";
            }
        }

        // Handle update action
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['update_id'])) {
            $updated = $db->updateExpense(
                $_POST['update_id'],
                $_POST['date'],
                $_POST['item'],
                $_POST['place'],
                $_POST['amount'],
                $_POST['type']
            );
            if ($updated) {
                echo "<p style='color: green;'>Expense updated successfully!</p>";
            } else {
                echo "<p style='color: red;'>Error updating expense.</p>";
            }
        }
                /*
    // Get expenses for the selected month
    $currentMonth = isset($_GET['month']) ? (int)$_GET['month'] : (int)date('n');
    $expenses = $db->getAllExpenses(); // Temporarily get all expenses to see dates
    
    // Debug output
    echo "<div style='background: #f0f0f0; padding: 10px; margin: 10px 0;'>";
    echo "Current Month Selected: " . $currentMonth . "<br><br>";
    echo "All dates in database:<br>";
    foreach ($expenses as $expense) {
        echo "Raw date value: [" . $expense['date'] . "]<br>";
    }
    echo "</div>";  */
    
    // Now get filtered expenses
    $currentType = isset($_GET['type']) ? $_GET['type'] : null;
    $expenses = $db->getExpensesByMonth($currentMonth, $currentType);
    
    // Debug output
    echo "<div style='background: #f0f0f0; padding: 10px; margin: 10px 0;'>";
    echo "Current Month: " . $currentMonth . "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
    if ($currentType) {
        echo "Type: " . htmlspecialchars($currentType) . "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
    }
    echo "Number of expenses found: " . count($expenses) . "<br>";
    echo "total amount: $" . number_format(array_sum(array_column($expenses, 'amount')), 2) . "<br>";
    echo "</div>";
    ?>
        <div class="table-container">
        <table id="expensesTable">
            <thead>
                <tr>
                    <th data-sort="date">Date</th>
                    <th data-sort="item">Item</th>
                    <th data-sort="place">Place</th>
                    <th data-sort="amount">Amount</th>
                    <th data-sort="type">Type</th>
                </tr>
            </thead>
            <tbody>
                <?php
            if (empty($expenses)) {
                echo "<tr><td colspan='6' style='text-align: center;'>No expenses found. Add your first expense to get started!</td></tr>";
            } else {
                foreach ($expenses as $expense) {
                    echo "<tr>";
                    // Split the date and time for display
                    $dateTime = explode(" ", $expense['date']);
                    $date = $dateTime[0];
                    $time = isset($dateTime[1]) && isset($dateTime[2]) ? $dateTime[1] . " " . $dateTime[2] : "";
                    echo "<td data-value='" . htmlspecialchars($expense['date']) . "'>" . 
                         htmlspecialchars($date) . 
                         ($time ? "<br><span style='font-size: 0.8em; color: #666;'>" . htmlspecialchars($time) . "</span>" : "") . 
                         "</td>";
                    echo "<td data-value='" . htmlspecialchars($expense['item']) . "'>" . htmlspecialchars($expense['item']) . "</td>";
                    echo "<td data-value='" . htmlspecialchars($expense['place']) . "'>" . htmlspecialchars($expense['place']) . "</td>";
                    echo "<td data-value='" . $expense['amount'] . "'>$" . number_format($expense['amount'], 2) . "</td>";
                    echo "<td data-value='" . htmlspecialchars($expense['type']) . "'>" . htmlspecialchars($expense['type']) . "</td>";
                    echo "</tr>";
                }
            }
            ?>
            </tbody>
        </table>
        </div>
    </section>
</body>
</html>
