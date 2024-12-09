<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="expenses_style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <title>Expenses</title>
</head>
<body>
    <h1><a href="#filterContainer">Expenses</a></h1>
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

    $expenses = $db->getAllExpenses();
    ?>
    <table id="expensesTable">
        <thead>
            <tr>
                <th data-sort="date">Date</th>
                <th data-sort="item">Item</th>
                <th data-sort="place">Place</th>
                <th data-sort="amount">Amount</th>
                <th data-sort="type">Type</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
        <?php
        if (empty($expenses)) {
            echo "<tr><td colspan='6' style='text-align: center;'>No expenses found. Add your first expense to get started!</td></tr>";
        } else {
            foreach ($expenses as $expense) {
                echo "<tr>";
                echo "<td data-value='" . htmlspecialchars($expense['date']) . "'>" . htmlspecialchars($expense['date']) . "</td>";
                echo "<td data-value='" . htmlspecialchars($expense['item']) . "'>" . htmlspecialchars($expense['item']) . "</td>";
                echo "<td data-value='" . htmlspecialchars($expense['place']) . "'>" . htmlspecialchars($expense['place']) . "</td>";
                echo "<td data-value='" . $expense['amount'] . "'>$" . number_format($expense['amount'], 2) . "</td>";
                echo "<td data-value='" . htmlspecialchars($expense['type']) . "'>" . htmlspecialchars($expense['type']) . "</td>";
                echo "<td class='action-buttons'>
                        <button onclick='openEditModal(" . json_encode($expense) . ")' class='edit-btn' title='Edit'><i class='fas fa-edit'></i></button>
                        <form method='POST' class='delete-form' onsubmit='return confirm(\"Are you sure you want to delete this expense?\");'>
                            <input type='hidden' name='delete_id' value='" . $expense['id'] . "'>
                            <button type='submit' class='delete-btn' title='Delete'><i class='fas fa-trash-alt'></i></button>
                        </form>
                    </td>";
                echo "</tr>";
            }
        }
        ?>
        </tbody>
    </table>

    <!-- Add filter inputs -->
    <details class="filter-container">
        <summary id="filterContainer">Filters</summary>
        <input type="text" id="dateFilter" placeholder="Filter by date">
        <input type="text" id="itemFilter" placeholder="Filter by item">
        <input type="text" id="placeFilter" placeholder="Filter by place">
        <input type="number" id="amountFilter" placeholder="Filter by amount">
        <select id="typeFilter">
            <option value="">Filter by type</option>
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
        <button onclick="clearFilters()">Clear Filters</button>
    </details>
    <div class="button-container">
        <a href="index.php">Back to Add Expense</a>
    </div>

    <!-- Edit Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeEditModal()">&times;</span>
            <h2>Edit Expense</h2>
            <div class="edit-form-container">
                <form method="POST">
                    <input type="hidden" name="update_id" id="edit_id">
                    <input type="text" name="date" id="edit_date" required>
                    <input type="text" name="item" id="edit_item" placeholder="Item" required>
                    <input type="text" name="place" id="edit_place" placeholder="Place" required>
                    <input type="number" step="1" name="amount" id="edit_amount" placeholder="Amount" required>
                    <select name="type" id="edit_type" required>
                        <option value="">Select Type</option>
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
                    <button type="submit">Update Expense</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        // Edit Modal Functions
        function openEditModal(expense) {
            document.getElementById('editModal').style.display = 'block';
            document.getElementById('edit_id').value = expense.id;
            document.getElementById('edit_date').value = expense.date;
            document.getElementById('edit_item').value = expense.item;
            document.getElementById('edit_place').value = expense.place;
            document.getElementById('edit_amount').value = expense.amount;
            document.getElementById('edit_type').value = expense.type;
        }

        function closeEditModal() {
            document.getElementById('editModal').style.display = 'none';
        }

        // Close modal when clicking outside of it
        window.onclick = function(event) {
            var modal = document.getElementById('editModal');
            if (event.target == modal) {
                closeEditModal();
            }
        }

        // Sorting Functions
        document.addEventListener('DOMContentLoaded', function() {
            const table = document.getElementById('expensesTable');
            const headers = table.querySelectorAll('th[data-sort]');
            let currentSort = { column: null, direction: 'asc' };

            headers.forEach(header => {
                header.addEventListener('click', () => {
                    const column = header.dataset.sort;
                    const isNumeric = column === 'amount';
                    
                    // Update sort direction
                    if (currentSort.column === column) {
                        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
                    } else {
                        currentSort = { column: column, direction: 'asc' };
                    }

                    // Update header classes
                    headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                    header.classList.add(`sort-${currentSort.direction}`);

                    // Get rows and sort
                    const tbody = table.querySelector('tbody');
                    const rows = Array.from(tbody.querySelectorAll('tr'));

                    // Skip if no data rows
                    if (rows.length <= 1 && rows[0].querySelector('td[colspan]')) {
                        return;
                    }

                    const sortedRows = rows.sort((a, b) => {
                        const aValue = a.querySelector(`td[data-value]:nth-child(${header.cellIndex + 1})`).dataset.value;
                        const bValue = b.querySelector(`td[data-value]:nth-child(${header.cellIndex + 1})`).dataset.value;

                        if (isNumeric) {
                            return currentSort.direction === 'asc' 
                                ? parseFloat(aValue) - parseFloat(bValue)
                                : parseFloat(bValue) - parseFloat(aValue);
                        } else {
                            return currentSort.direction === 'asc'
                                ? aValue.localeCompare(bValue)
                                : bValue.localeCompare(aValue);
                        }
                    });

                    // Clear and append sorted rows
                    while (tbody.firstChild) {
                        tbody.removeChild(tbody.firstChild);
                    }
                    tbody.append(...sortedRows);
                });
            });
        });

        // Add filter functionality
        function applyFilters() {
            const dateFilter = document.getElementById('dateFilter').value.toLowerCase();
            const itemFilter = document.getElementById('itemFilter').value.toLowerCase();
            const placeFilter = document.getElementById('placeFilter').value.toLowerCase();
            const amountFilter = document.getElementById('amountFilter').value;
            const typeFilter = document.getElementById('typeFilter').value.toLowerCase();

            const rows = document.querySelectorAll('#expensesTable tbody tr');

            rows.forEach(row => {
                const date = row.cells[0].getAttribute('data-value').toLowerCase();
                const item = row.cells[1].getAttribute('data-value').toLowerCase();
                const place = row.cells[2].getAttribute('data-value').toLowerCase();
                const amount = row.cells[3].getAttribute('data-value');
                const type = row.cells[4].getAttribute('data-value').toLowerCase();

                const dateMatch = !dateFilter || date.includes(dateFilter);
                const itemMatch = !itemFilter || item.includes(itemFilter);
                const placeMatch = !placeFilter || place.includes(placeFilter);
                const amountMatch = !amountFilter || amount === amountFilter;
                const typeMatch = !typeFilter || type === typeFilter;

                if (dateMatch && itemMatch && placeMatch && amountMatch && typeMatch) {
                    row.classList.remove('hidden');
                } else {
                    row.classList.add('hidden');
                }
            });
        }

        function clearFilters() {
            document.getElementById('dateFilter').value = '';
            document.getElementById('itemFilter').value = '';
            document.getElementById('placeFilter').value = '';
            document.getElementById('amountFilter').value = '';
            document.getElementById('typeFilter').value = '';
            applyFilters();
        }

        // Add event listeners for filter inputs
        document.getElementById('dateFilter').addEventListener('input', applyFilters);
        document.getElementById('itemFilter').addEventListener('input', applyFilters);
        document.getElementById('placeFilter').addEventListener('input', applyFilters);
        document.getElementById('amountFilter').addEventListener('input', applyFilters);
        document.getElementById('typeFilter').addEventListener('change', applyFilters);
    </script>
</body>
</html>