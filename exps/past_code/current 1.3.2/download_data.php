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
    foreach ($result as $row) {
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

    /* Modal styles */
    .modal {
        display: none;
        position: fixed;
        z-index: 1;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.4);
    }

    .modal-content {
        background-color: #fefefe;
        margin: 15% auto;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
        max-width: 500px;
        border-radius: 5px;
        position: relative;
    }

    .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
    }

    .close:hover {
        color: black;
    }

    .detail-row {
        margin: 10px 0;
        padding: 5px 0;
        border-bottom: 1px solid #eee;
    }

    .detail-label {
        font-weight: bold;
        margin-right: 10px;
        display: inline-block;
        width: 80px;
    }

    .detail-value {
        display: inline-block;
    }

    tbody tr {
        cursor: pointer;
    }

    tbody tr:hover {
        background-color: #f5f5f5;
    }

    .edit-mode input {
        width: calc(100% - 100px);
        padding: 5px;
        margin: 2px 0;
        border: 1px solid #ddd;
        border-radius: 3px;
    }

    .button-group {
        margin-top: 20px;
        text-align: right;
    }

    .button-group button {
        padding: 8px 15px;
        margin-left: 10px;
        border: none;
        border-radius: 3px;
        cursor: pointer;
    }

    .edit-btn {
        background-color: #4CAF50;
        color: white;
    }

    .save-btn {
        background-color: #4CAF50;
        color: white;
    }

    .cancel-btn {
        background-color: #f44336;
        color: white;
    }

    .success-message {
        color: #4CAF50;
        margin-top: 10px;
        text-align: center;
    }

    .error-message {
        color: #f44336;
        margin-top: 10px;
        text-align: center;
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

    // Modal functionality
    function showDetails(id, date, item, place, amount, type, year) {
        const modal = document.getElementById('detailsModal');
        const modalContent = document.getElementById('modalContent');
        
        modalContent.innerHTML = `
            <span class="close">&times;</span>
            <h2>Expense Details</h2>
            <div class="detail-container">
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    <span class="detail-value" data-field="date">${date}</span>
                    <input type="datetime-local" class="edit-input" style="display:none" value="${formatDateForInput(date)}">
                </div>
                <div class="detail-row">
                    <span class="detail-label">Item:</span>
                    <span class="detail-value" data-field="item">${item}</span>
                    <input type="text" class="edit-input" style="display:none" value="${item}">
                </div>
                <div class="detail-row">
                    <span class="detail-label">Place:</span>
                    <span class="detail-value" data-field="place">${place}</span>
                    <input type="text" class="edit-input" style="display:none" value="${place}">
                </div>
                <div class="detail-row">
                    <span class="detail-label">Amount:</span>
                    <span class="detail-value" data-field="amount">$${amount}</span>
                    <input type="number" step="0.01" class="edit-input" style="display:none" value="${amount}">
                </div>
                <div class="detail-row">
                    <span class="detail-label">Type:</span>
                    <span class="detail-value" data-field="type">${type}</span>
                    <input type="text" class="edit-input" style="display:none" value="${type}">
                </div>
                <div class="detail-row">
                    <span class="detail-label">Year:</span>
                    <span class="detail-value">${year}</span>
                </div>
            </div>
            <div class="button-group">
                <button class="edit-btn" onclick="toggleEdit(this)">Edit</button>
                <button class="save-btn" style="display:none" onclick="saveChanges(${id})">Save</button>
                <button class="cancel-btn" style="display:none" onclick="cancelEdit()">Cancel</button>
            </div>
            <div id="statusMessage"></div>
        `;

        modal.style.display = 'block';

        // Close button functionality
        const closeBtn = modalContent.querySelector('.close');
        closeBtn.onclick = function() {
            modal.style.display = 'none';
        }

        // Click outside to close
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }

    function formatDateForInput(dateStr) {
        const date = new Date(dateStr);
        return date.toISOString().slice(0, 16);
    }

    function toggleEdit(btn) {
        const container = document.querySelector('.detail-container');
        const editBtn = btn;
        const saveBtn = document.querySelector('.save-btn');
        const cancelBtn = document.querySelector('.cancel-btn');
        
        container.querySelectorAll('.detail-value').forEach(span => {
            span.style.display = 'none';
        });
        
        container.querySelectorAll('.edit-input').forEach(input => {
            input.style.display = 'inline-block';
        });
        
        editBtn.style.display = 'none';
        saveBtn.style.display = 'inline-block';
        cancelBtn.style.display = 'inline-block';
    }

    function cancelEdit() {
        const container = document.querySelector('.detail-container');
        const editBtn = document.querySelector('.edit-btn');
        const saveBtn = document.querySelector('.save-btn');
        const cancelBtn = document.querySelector('.cancel-btn');
        
        container.querySelectorAll('.detail-value').forEach(span => {
            span.style.display = 'inline-block';
        });
        
        container.querySelectorAll('.edit-input').forEach(input => {
            input.style.display = 'none';
        });
        
        editBtn.style.display = 'inline-block';
        saveBtn.style.display = 'none';
        cancelBtn.style.display = 'none';
    }

    function saveChanges(id) {
        const inputs = document.querySelectorAll('.edit-input');
        const formData = new FormData();
        
        formData.append('id', id);
        inputs.forEach(input => {
            const field = input.previousElementSibling.getAttribute('data-field');
            let value = input.value;
            if (field === 'date') {
                value = new Date(value).toISOString();
            }
            formData.append(field, value);
        });

        fetch('update_expense.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const messageDiv = document.getElementById('statusMessage');
            if (data.success) {
                messageDiv.className = 'success-message';
                messageDiv.textContent = data.message;
                // Update the displayed values
                inputs.forEach(input => {
                    const field = input.previousElementSibling.getAttribute('data-field');
                    let displayValue = input.value;
                    if (field === 'amount') {
                        displayValue = '$' + displayValue;
                    }
                    input.previousElementSibling.textContent = displayValue;
                });
                // Return to view mode
                cancelEdit();
                // Reload the page after a short delay
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                messageDiv.className = 'error-message';
                messageDiv.textContent = data.message;
            }
        })
        .catch(error => {
            const messageDiv = document.getElementById('statusMessage');
            messageDiv.className = 'error-message';
            messageDiv.textContent = 'An error occurred while saving changes';
        });
    }
    </script>
</head>

<body>
    <!-- Add modal dialog structure -->
    <div id="detailsModal" class="modal">
        <div id="modalContent" class="modal-content">
        </div>
    </div>
    <div class="download-links">
        <a href="download_data.php?format=csv">Download Data CSV</a>
        <select name="year" id="yearSelect" onchange="updateView()">
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
                foreach ($result as $row):
                    $rowYear = date('Y', strtotime($row['date']));
                    $rowMonth = date('m', strtotime($row['date']));
                    // Skip if year is selected and doesn't match
                    if ($selectedYear && $rowYear !== $selectedYear) continue;
                    // Skip if month is selected and doesn't match
                    if ($selectedMonth && $rowMonth !== $selectedMonth) continue;
                    $totalAmount += $row['amount'];
                ?>
            <tr onclick="showDetails(
                <?php echo $row['id']; ?>,
                '<?php echo date('Y-M-j h:i:a', strtotime($row['date'])); ?>', 
                '<?php echo addslashes(htmlspecialchars($row['item'])); ?>', 
                '<?php echo addslashes(htmlspecialchars($row['place'])); ?>', 
                '<?php echo number_format($row['amount'], 2); ?>', 
                '<?php echo addslashes(htmlspecialchars($row['type'])); ?>', 
                '<?php echo date('Y', strtotime($row['date'])); ?>'
            )">
                <td class="date"><?php echo date('M-j h:i:a', strtotime($row['date'])); ?></td>
                <td><?php echo htmlspecialchars($row['item']); ?></td>
                <td><?php echo htmlspecialchars($row['place']); ?></td>
                <td class="amount">$<?php echo number_format($row['amount'], 2); ?></td>
                <td><?php echo htmlspecialchars($row['type']); ?></td>
                <td><?php echo date('Y', strtotime($row['date'])); ?></td>
            </tr>
            <?php endforeach; ?>
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