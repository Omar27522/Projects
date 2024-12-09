<?php
require_once 'db_connect.php';

// Initialize database connection
$db = new Database();
$format = $_GET['format'] ?? 'html';
$type = $_GET['type'] ?? 'yearly';
$selectedYear = $_GET['year'] ?? '';
$selectedMonth = $_GET['month'] ?? '';

if ($format === 'csv') {
    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="expenses_' . ($selectedYear ?: 'all') . ($selectedMonth ? '_' . $months[$selectedMonth] : '') . '.csv"');
    
    $output = fopen('php://output', 'w');
    
    // Write headers
    fputcsv($output, ['Date', 'Item', 'Place', 'Amount', 'Type', 'Year']);
    
    // Get and write data
    $result = $db->getYearlyExpenses();
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $rowYear = date('Y', strtotime($row['date']));
        $rowMonth = date('m', strtotime($row['date']));
        
        // Skip if year is selected and doesn't match
        if ($selectedYear && $rowYear !== $selectedYear) continue;
        // Skip if month is selected and doesn't match
        if ($selectedMonth && $rowMonth !== $selectedMonth) continue;
        
        fputcsv($output, [
            date('Y-M-j h:i:a', strtotime($row['date'])),
            $row['item'],
            $row['place'],
            $row['amount'],
            $row['type'],
            date('Y', strtotime($row['date']))
        ]);
    }
    
    fclose($output);
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Download Expenses Data</title>
    <style>
        .download-links {
            margin: 20px 0;
        }
        .download-links a {
            margin-right: 10px;
            padding: 5px 10px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 3px;
        }
        .download-links select {
            width: 30%;
            margin-right: 10px;
            padding: 5px 10px;
            border-radius: 3px;
        }
        .amount {
            text-align: right;
        }
        .date {
            white-space: nowrap;
        }
    </style>
    <script>
        function updateView() {
            var year = document.getElementById('yearSelect').value;
            var month = document.getElementById('monthSelect').value;
            if (year !== 'View Yearly Data') {
                window.location.href = 'download_data.php?year=' + year + (month !== '' ? '&month=' + month : '');
            }
        }
    </script>
</head>
<body>
    <div class="download-links">
        <a href="download_data.php?format=csv">Download Data CSV</a>
        <select name="year" id="yearSelect" onchange="updateView()">
            
        
        <?php
        if(isset($_GET['year=2024'])) {
            echo "";
        }
        else{
            echo"";
        }
        ?>
        <option>View Yearly Data</option>
            <option value="2024">2024</option>
                <option value="2025">2025</option>
            
        </select>
        <select name="month" id="monthSelect" onchange="updateView()">
            <option value="">Select Month</option>
            <?php
            $months = [
                '01' => 'January', '02' => 'February', '03' => 'March',
                '04' => 'April', '05' => 'May', '06' => 'June',
                '07' => 'July', '08' => 'August', '09' => 'September',
                '10' => 'October', '11' => 'November', '12' => 'December'
            ];
            foreach ($months as $num => $name):
            ?>
                <option value="<?php echo $num; ?>" <?php echo $num === $selectedMonth ? 'selected' : ''; ?>>
                    <?php echo $name; ?>
                </option>
            <?php endforeach; ?>
        </select><a style="display:inline;float:right;" href="monthly.php">Back</a>
    </div>

    <?php if ($format === 'html'): ?>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Item</th>
                    <th>Place</th>
                    <th>Amount</th>
                    <th>Type</th>
                    <th>Year</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $result = $db->getYearlyExpenses();
                $totalAmount = 0;
                while ($row = $result->fetchArray(SQLITE3_ASSOC)):
                    $rowYear = date('Y', strtotime($row['date']));
                    $rowMonth = date('m', strtotime($row['date']));
                    
                    // Skip if year is selected and doesn't match
                    if ($selectedYear && $rowYear !== $selectedYear) continue;
                    // Skip if month is selected and doesn't match
                    if ($selectedMonth && $rowMonth !== $selectedMonth) continue;
                    
                    $totalAmount += $row['amount'];
                ?>
                <tr>
                    <td class="date"><?php echo date('Y-M-j h:i:a', strtotime($row['date'])); ?></td>
                    <td><?php echo htmlspecialchars($row['item']); ?></td>
                    <td><?php echo htmlspecialchars($row['place']); ?></td>
                    <td class="amount">$<?php echo number_format($row['amount'], 2); ?></td>
                    <td><?php echo htmlspecialchars($row['type']); ?></td>
                    <td><?php echo date('Y', strtotime($row['date'])); ?></td>
                </tr>
                <?php endwhile; ?>
                <tr>
                    <td colspan="3"><strong>Total</strong></td>
                    <td class="amount"><strong>$<?php echo number_format($totalAmount, 2); ?></strong></td>
                    <td colspan="2"></td>
                </tr>
            </tbody>
        </table>
    <?php endif; ?>
</body>
</html>