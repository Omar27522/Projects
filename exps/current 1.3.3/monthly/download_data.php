<?php
require_once '../db_connect.php';

// Initialize database connection and variables
$db = new Database();
$format = $_GET['format'] ?? 'html';
$type = $_GET['type'] ?? 'yearly';
$selectedYear = $_GET['year'] ?? date('Y');
$selectedMonth = $_GET['month'] ?? '';
$action = $_POST['action'] ?? '';
$message = '';
$error = '';

// Handle form submissions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if ($action === 'update') {
        $id = $_POST['id'] ?? '';
        $date = $_POST['date'] ?? '';
        $item = $_POST['item'] ?? '';
        $place = $_POST['place'] ?? '';
        $amount = $_POST['amount'] ?? '';
        $type = $_POST['type'] ?? '';
        
        if ($id && $date && $item && $amount) {
            try {
                $result = $db->updateExpense($id, $date, $item, $place, $amount, $type);
                if ($result) {
                    $message = "Record updated successfully!";
                } else {
                    $error = "Failed to update record";
                }
            } catch (Exception $e) {
                $error = "Error updating record: " . $e->getMessage();
            }
        }
    }
}

// Get sort parameters
$sortBy = $_POST['sort'] ?? 'date';
$sortOrder = $_POST['order'] ?? 'desc';

// Handle CSV download
if ($format === 'csv') {
    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="expenses_' . ($selectedYear ?: 'all') . ($selectedMonth ? '_' . date('F', mktime(0, 0, 0, $selectedMonth, 1)) : '') . '.csv"');
    $output = fopen('php://output', 'w');
    fputcsv($output, ['Date', 'Item', 'Place', 'Amount', 'Type', 'Year']);
    $result = $db->getYearlyExpenses();
    foreach ($result as $row) {
        $rowYear = date('Y', strtotime($row['date']));
        $rowMonth = date('m', strtotime($row['date']));
        if ($selectedYear && $rowYear !== $selectedYear) continue;
        if ($selectedMonth && $rowMonth !== $selectedMonth) continue;
        fputcsv($output, [
            date('M j', strtotime($row['date'])),
            $row['item'],
            $row['place'],
            $row['amount'],
            $row['type'],
            $rowYear
        ]);
    }
    fclose($output);
    exit();
}

// Get data for display
$expenses = $db->getYearlyExpenses();
$filteredExpenses = array_filter($expenses, function($row) use ($selectedYear, $selectedMonth) {
    $rowYear = date('Y', strtotime($row['date']));
    $rowMonth = date('m', strtotime($row['date']));
    
    if ($selectedYear && $rowYear !== $selectedYear) return false;
    if ($selectedMonth && $rowMonth !== $selectedMonth) return false;
    return true;
});

// Sort the filtered expenses
usort($filteredExpenses, function($a, $b) use ($sortBy, $sortOrder) {
    $aVal = $sortBy === 'date' ? strtotime($a[$sortBy]) : $a[$sortBy];
    $bVal = $sortBy === 'date' ? strtotime($b[$sortBy]) : $b[$sortBy];
    
    if ($sortBy === 'amount') {
        $aVal = floatval($aVal);
        $bVal = floatval($bVal);
    }
    
    if ($aVal == $bVal) return 0;
    
    if ($sortOrder === 'asc') {
        return $aVal > $bVal ? 1 : -1;
    } else {
        return $aVal < $bVal ? 1 : -1;
    }
});

?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="monthly.css">
    <title>Download Expenses Data</title>
</head>

<body>
    <div class="container"><div class="links">
        <h1>Download Expenses Data</h1>
        <?php links(); echo"</div>"; if ($message): ?>
        <div class="success-message"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>
        <?php if ($error): ?>
        <div class="error-message"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>

        <div class="download-links">
            <form method="get" action="">
                <select name="year">
                    <option value="">All Years</option>
                    <?php
                    $years = array_unique(array_map(function($row) {
                        return date('Y', strtotime($row['date']));
                    }, $expenses));
                    sort($years);
                    foreach ($years as $year): ?>
                    <option value="<?php echo $year; ?>" <?php echo $selectedYear == $year ? 'selected' : ''; ?>>
                        <?php echo $year; ?>
                    </option>
                    <?php endforeach; ?>
                </select>

                <select name="month">
                    <option value="">All Months</option>
                    <?php for ($i = 1; $i <= 12; $i++): ?>
                    <option value="<?php echo $i; ?>" <?php echo $selectedMonth == $i ? 'selected' : ''; ?>>
                        <?php echo date('F', mktime(0, 0, 0, $i, 1)); ?>
                    </option>
                    <?php endfor; ?>
                </select>

                <button type="submit">Filter</button>
                <a
                    href="?format=csv<?php echo $selectedYear ? '&year=' . $selectedYear : ''; ?><?php echo $selectedMonth ? '&month=' . $selectedMonth : ''; ?>">
                    Download CSV
                </a>
            </form>
            <div class="sort-form" id="sort-form">
                <form method="post" action="">
                   <h3 style="padding: 0;margin: 0"> Sort by:</h3>
                    <select name="sort">
                        <option value="date" <?php echo $sortBy === 'date' ? 'selected' : ''; ?>>Date</option>
                        <option value="amount" <?php echo $sortBy === 'amount' ? 'selected' : ''; ?>>Amount</option>
                        <option value="type" <?php echo $sortBy === 'type' ? 'selected' : ''; ?>>Type</option>
                        <option value="place" <?php echo $sortBy === 'place' ? 'selected' : ''; ?>>Place</option>
                        <option value="item" <?php echo $sortBy === 'item' ? 'selected' : ''; ?>>Item</option>
                    </select>
                    <div class="order-radio">
                        <input type="radio" id="asc" name="order" value="asc" <?php echo $sortOrder === 'asc' ? 'checked' : ''; ?>>
                        <label for="asc">&#9650;</label>
                        <input type="radio" id="desc" name="order" value="desc" <?php echo $sortOrder === 'desc' ? 'checked' : ''; ?>>
                        <label for="desc">&#9660;</label>
                    </div>
                    <button type="submit">Sort</button>
                </form>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Item</th>
                    <th>Place</th>
                    <th>$</th>
                    <th>Type</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($filteredExpenses as $row): ?>
                <tr>
                    <td class="date"><?php echo date('M j', strtotime($row['date'])); ?></td>
                    <td><?php echo htmlspecialchars($row['item']); ?></td>
                    <td><?php echo htmlspecialchars($row['place']); ?></td>
                    <td class="amount"><?php echo htmlspecialchars($row['amount']); ?></td>
                    <td><?php echo htmlspecialchars($row['type']); ?></td>
                    <td>
                        <form method="post" action="">
                            <input type="hidden" name="action" value="update">
                            <input type="hidden" name="id" value="<?php echo $row['id']; ?>">
                            <button type="button"
                                onclick="showEditForm(this.form, <?php echo htmlspecialchars(json_encode($row)); ?>)">Edit</button>
                        </form>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>

    <!-- Edit Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2>Edit Expense</h2>
            <form method="post" action="" id="editForm">
                <input type="hidden" name="action" value="update">
                <input type="hidden" name="id" id="editId">
                <div class="detail-row">
                    <label class="detail-label">Date:</label>
                    <input type="date" name="date" id="editDate" required>
                </div>

                <div class="detail-row">
                    <label class="detail-label">Item:</label>
                    <input type="text" name="item" id="editItem" required>
                </div>

                <div class="detail-row">
                    <label class="detail-label">Place:</label>
                    <input type="text" name="place" id="editPlace">
                </div>

                <div class="detail-row">
                    <label class="detail-label">Amount:</label>
                    <input type="number" step="0.01" name="amount" id="editAmount" required>
                </div>

                <div class="detail-row">
                    <label class="detail-label">Type:</label>
                    <input type="text" name="type" id="editType">
                </div>

                <div class="button-group">
                    <button type="button" class="cancel-btn" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="save-btn">Save Changes</button>
                </div>
            </form>
        </div>
    </div>

    <script>
    function showEditForm(form, data) {
        document.getElementById('editId').value = data.id;
        document.getElementById('editDate').value = data.date;
        document.getElementById('editItem').value = data.item;
        document.getElementById('editPlace').value = data.place;
        document.getElementById('editAmount').value = data.amount;
        document.getElementById('editType').value = data.type;
        document.getElementById('editModal').style.display = 'block';
    }

    function closeModal() {
        document.getElementById('editModal').style.display = 'none';
    }

    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target == document.getElementById('editModal')) {
            closeModal();
        }
    }
    </script>
    <?php footer();?>
</body>
</html>