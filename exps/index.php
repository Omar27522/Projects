<?php
// Initialize default values
$config = ['items' => []];
$expenses = ['expenses' => []];

// Helper function to format date
function formatDate($dateStr) {
    $date = new DateTime($dateStr);
    return $date->format('j-M');
}

// Load configuration and expenses data
try {
    if (file_exists('config.json')) {
        $configData = file_get_contents('config.json');
        $config = json_decode($configData, true) ?: ['items' => []];
    }
    
    if (file_exists('expenses.json')) {
        $expensesData = file_get_contents('expenses.json');
        $expenses = json_decode($expensesData, true) ?: ['expenses' => []];
    }
} catch (Exception $e) {
    error_log("Error loading data: " . $e->getMessage());
}

// Get unique places from expenses
$uniquePlaces = array_unique(array_map(function($expense) {
    return $expense['place'];
}, $expenses['expenses']));

// Get unique types combining both config categories and expense types
$uniqueTypes = array_unique(array_merge(
    array_map(function($item) { return $item['category']; }, $config['items']),
    array_map(function($expense) { return $expense['type']; }, $expenses['expenses'])
));

// Sort arrays alphabetically
sort($uniquePlaces);
sort($uniqueTypes);

// Sort items alphabetically
if (!empty($config['items'])) {
    usort($config['items'], function($a, $b) {
        return strcasecmp($a['name'], $b['name']);
    });
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expenses Tracker</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="style.css" type="text/css">
    <style>
        .table-container {
            width: 100%;
            max-width: 1200px;
            overflow-x: auto;
            margin: 0 auto 1em;
            padding: 0 1rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        th, td {
            padding: 12px;
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background-color: #4299e1;
            color: white;
            font-weight: 500;
            position: sticky;
            top: 0;
            z-index: 1;
        }

        tr:hover td {
            background-color: #f7fafc;
        }

        /* Column widths */
        th:nth-child(1), td:nth-child(1) { width: 12%; } /* Date */
        th:nth-child(2), td:nth-child(2) { width: 25%; } /* Item */
        th:nth-child(3), td:nth-child(3) { width: 25%; } /* Place */
        th:nth-child(4), td:nth-child(4) { width: 12%; } /* Amount */
        th:nth-child(5), td:nth-child(5) { width: 15%; } /* Type */
        th:nth-child(6), td:nth-child(6) { width: 11%; } /* Actions */

        .action-buttons {
            white-space: nowrap;
            text-align: center;
        }

        .action-buttons button {
            border: none;
            background: none;
            cursor: pointer;
            padding: 5px;
            margin: 0 2px;
            transition: all 0.2s ease;
        }

        .action-buttons button:hover {
            transform: scale(1.1);
        }

        .edit-btn i {
            color: #28a745;
        }

        .delete-btn i {
            color: #dc3545;
        }

        .edit-mode input {
            width: 100%;
            padding: 8px;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            font-family: inherit;
        }

        .edit-mode input:focus {
            outline: none;
            border-color: #4299e1;
            box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.2);
        }

        @media (max-width: 768px) {
            .table-container {
                padding: 0 0.5rem;
            }
            
            th, td {
                padding: 8px;
            }
        }

        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
        }

        .modal-tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 1rem;
        }

        .tab-btn {
            padding: 0.5rem 1rem;
            border: none;
            background: none;
            color: #718096;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .tab-btn.active {
            color: #4299e1;
            border-bottom: 2px solid #4299e1;
        }

        .tab-btn:hover {
            color: #4299e1;
        }
    </style>
    <script>
        // Store all data for autofill
        const itemsData = <?php echo json_encode($config['items']); ?>;
        const expensesData = <?php echo json_encode($expenses['expenses']); ?>;

        // Date formatting function
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            const day = date.getDate();
            const month = date.toLocaleString('en-US', { month: 'short' });
            return `${day}-${month}`;
        }

        function openModal() {
            document.getElementById('expenseModal').style.display = 'block';
            resetForm();
        }

        function closeModal() {
            document.getElementById('expenseModal').style.display = 'none';
            resetForm();
        }

        function resetForm() {
            document.getElementById('expenseForm').reset();
            document.querySelectorAll('.form-step').forEach(step => step.classList.remove('active'));
            document.getElementById('dateStep').classList.add('active');
            
            // Pre-fill today's date
            const today = new Date();
            document.getElementById('date').value = today.toISOString().split('T')[0];
            
            // Reset tabs
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector('.tab-btn').classList.add('active');
            
            // Reset tab content
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById('expenseTab').classList.add('active');
        }

        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.toLowerCase().includes(tabName)) {
                    btn.classList.add('active');
                }
            });
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabName + 'Tab').classList.add('active');
        }

        function nextStep(currentId, nextId) {
            // Validate current step
            const currentInputs = document.getElementById(currentId).querySelectorAll('input[required]');
            let isValid = true;
            currentInputs.forEach(input => {
                if (!input.value) {
                    isValid = false;
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
            });
            
            if (!isValid) return;

            // If moving to review step, update review content
            if (nextId === 'reviewStep') {
                updateReviewContent();
            }

            // Switch steps
            document.getElementById(currentId).classList.remove('active');
            const nextStep = document.getElementById(nextId);
            nextStep.classList.add('active');

            // Focus on the first input field in the next step
            const nextInput = nextStep.querySelector('input');
            if (nextInput && nextId !== 'reviewStep') {
                nextInput.focus();
            }
        }

        function prevStep(currentId, prevId) {
            document.getElementById(currentId).classList.remove('active');
            document.getElementById(prevId).classList.add('active');
        }

        function updateReviewContent() {
            const date = new Date(document.getElementById('date').value);
            document.getElementById('reviewDate').textContent = formatDate(date);
            document.getElementById('reviewItem').textContent = document.getElementById('item').value;
            document.getElementById('reviewPlace').textContent = document.getElementById('place').value;
            document.getElementById('reviewAmount').textContent = '$' + parseFloat(document.getElementById('amount').value).toFixed(2);
            document.getElementById('reviewType').textContent = document.getElementById('type').value;
        }

        function submitExpense() {
            const formData = new FormData(document.getElementById('expenseForm'));
            const data = Object.fromEntries(formData.entries());
            
            fetch('add_expense.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error adding expense: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding expense: ' + error.message);
            });
        }

        // Initialize when document is ready
        document.addEventListener('DOMContentLoaded', function() {
            // Pre-fill today's date
            const today = new Date();
            document.getElementById('date').value = today.toISOString().split('T')[0];

            // Add keypress event listener for form navigation
            document.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault(); // Prevent default form submission
                    
                    const currentStep = document.querySelector('.form-step.active');
                    if (!currentStep) return;

                    // If we're on the review step, submit the form
                    if (currentStep.id === 'reviewStep') {
                        submitExpense();
                        return;
                    }

                    // For other steps, trigger the next button click
                    const nextBtn = currentStep.querySelector('.next-btn');
                    if (nextBtn) {
                        nextBtn.click();
                    }
                }
            });
            
            // Add event listeners for next buttons
            document.querySelectorAll('.next-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const currentStep = this.closest('.form-step');
                    const nextStep = currentStep.nextElementSibling;
                    if (nextStep) {
                        currentStep.classList.remove('active');
                        nextStep.classList.add('active');
                        updateReviewContent();
                        
                        // Focus on the first input field in the next step
                        const nextInput = nextStep.querySelector('input');
                        if (nextInput && !nextStep.id.includes('review')) {
                            nextInput.focus();
                        }
                    }
                });
            });

            // Add event listeners for back buttons
            document.querySelectorAll('.back-btn').forEach(button => {
                button.addEventListener('click', () => {
                    const currentStep = button.closest('.form-step');
                    const previousStep = currentStep.previousElementSibling;
                    
                    if (previousStep) {
                        currentStep.classList.remove('active');
                        previousStep.classList.add('active');
                    }
                });
            });

            // Add enter key support for next step
            document.querySelectorAll('.form-step input').forEach(input => {
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        const currentStep = this.closest('.form-step');
                        const nextBtn = currentStep.querySelector('.next-btn');
                        if (nextBtn) {
                            nextBtn.click();
                        }
                    }
                });
            });

            // Add click event listener for the new entry button
            const newEntryBtn = document.querySelector('.new-entry-btn');
            if (newEntryBtn) {
                newEntryBtn.addEventListener('click', openModal);
            }

            // Format existing dates in the table
            const dateColumns = document.querySelectorAll('td:first-child:not(.empty-row td)');
            dateColumns.forEach(cell => {
                if (cell.textContent.trim()) {
                    cell.textContent = formatDate(cell.textContent);
                }
            });
        });
    </script>
</head>
<body>
<h1>Expenses</h1>

<div class='table-container'>
<table>
<tr>
<th>Date</th>
<th>Item</th>
<th>Place</th>
<th>Amount</th>
<th>Type</th>
<th>Actions</th>
</tr>

<tbody>
<?php if (empty($expenses['expenses'])): ?>
    <tr class="empty-row">
        <td colspan="6" style="text-align: center; padding: 20px; color: #666;">
            No expenses found. Click the "Add Expense" button to add one.
        </td>
    </tr>
<?php else: ?>
    <?php foreach ($expenses['expenses'] as $index => $expense): ?>
        <tr>
            <td><?= htmlspecialchars(formatDate($expense['date'])) ?></td>
            <td><?= htmlspecialchars($expense['item']) ?></td>
            <td><?= htmlspecialchars($expense['place']) ?></td>
            <td><?= htmlspecialchars($expense['amount']) ?></td>
            <td><?= htmlspecialchars($expense['type']) ?></td>
            <td>
                <div class="action-buttons">
                    <button class="edit-btn" data-action="edit"><i class="fas fa-edit"></i></button>
                    <button class="delete-btn" data-action="delete"><i class="fas fa-trash"></i></button>
                </div>
            </td>
        </tr>
    <?php endforeach; ?>
<?php endif; ?>
</tbody>
</table>
</div>
<button class="new-entry-btn" data-action="new">
    <i class="fas fa-plus"></i> Add Entry
</button>

<!-- Modal Form -->
<div class="modal" id="expenseModal">
    <div class="modal-content">
        <div class="modal-tabs">
            <button class="tab-btn active" onclick="switchTab('expense')">New Expense</button>
            <button class="tab-btn" onclick="switchTab('items')">Manage Items</button>
        </div>

        <!-- New Expense Tab -->
        <div id="expenseTab" class="tab-content active">
            <form id="expenseForm" onsubmit="event.preventDefault(); submitExpense();">
                <div class="form-steps">
                    <!-- Step 1: Date -->
                    <div class="form-step active" id="dateStep">
                        <div class="form-group full-container">
                            <label for="date">Date:</label>
                            <input type="text" id="date" name="date" required autocomplete="off" tabindex="1">
                        </div>
                        <div class="button-group">
                            <button type="button" class="next-btn" tabindex="2">Next</button>
                        </div>
                    </div>

                    <!-- Step 2: Item -->
                    <div class="form-step" id="itemStep">
                        <div class="form-group full-container">
                            <label for="item">Item:</label>
                            <input type="text" id="item" name="item" list="items" required autocomplete="off" tabindex="3">
                            <datalist id="items">
                                <?php foreach ($config['items'] as $item): ?>
                                    <option value="<?= htmlspecialchars($item['name']) ?>">
                                <?php endforeach; ?>
                            </datalist>
                        </div>
                        <div class="button-group">
                            <button type="button" class="back-btn" tabindex="5">Back</button>
                            <button type="button" class="next-btn" tabindex="4">Next</button>
                        </div>
                    </div>

                    <!-- Step 3: Place -->
                    <div class="form-step" id="placeStep">
                        <div class="form-group full-container">
                            <label for="place">Place:</label>
                            <input type="text" id="place" name="place" list="places" required autocomplete="off" tabindex="6">
                            <datalist id="places">
                                <?php foreach ($uniquePlaces as $place): ?>
                                    <option value="<?= htmlspecialchars($place) ?>">
                                <?php endforeach; ?>
                            </datalist>
                        </div>
                        <div class="button-group">
                            <button type="button" class="back-btn" tabindex="8">Back</button>
                            <button type="button" class="next-btn" tabindex="7">Next</button>
                        </div>
                    </div>

                    <!-- Step 4: Amount -->
                    <div class="form-step" id="amountStep">
                        <div class="form-group full-container">
                            <label for="amount">Amount:</label>
                            <input type="number" id="amount" name="amount" step="0.01" required autocomplete="off" tabindex="9">
                        </div>
                        <div class="button-group">
                            <button type="button" class="back-btn" tabindex="11">Back</button>
                            <button type="button" class="next-btn" tabindex="10">Next</button>
                        </div>
                    </div>

                    <!-- Step 5: Type -->
                    <div class="form-step" id="typeStep">
                        <div class="form-group full-container">
                            <label for="type">Type:</label>
                            <input type="text" id="type" name="type" list="types" required autocomplete="off" tabindex="12">
                            <datalist id="types">
                                <?php foreach ($uniqueTypes as $type): ?>
                                    <option value="<?= htmlspecialchars($type) ?>">
                                <?php endforeach; ?>
                            </datalist>
                        </div>
                        <div class="button-group">
                            <button type="button" class="back-btn" tabindex="14">Back</button>
                            <button type="button" class="next-btn" tabindex="13">Next</button>
                        </div>
                    </div>

                    <!-- Step 6: Review -->
                    <div class="form-step" id="reviewStep">
                        <h3>Review Your Expense</h3>
                        <div class="review-content">
                            <p><strong>Date:</strong> <span id="reviewDate"></span></p>
                            <p><strong>Item:</strong> <span id="reviewItem"></span></p>
                            <p><strong>Place:</strong> <span id="reviewPlace"></span></p>
                            <p><strong>Amount:</strong> $<span id="reviewAmount"></span></p>
                            <p><strong>Type:</strong> <span id="reviewType"></span></p>
                        </div>
                        <div class="button-group">
                            <button type="button" class="back-btn" tabindex="16">Back</button>
                            <button type="submit" class="submit-btn" tabindex="15">Submit</button>
                        </div>
                    </div>
                </div>
            </form>
        </div>

        <!-- Manage Items Tab -->
        <div id="itemsTab" class="tab-content">
            <div class="items-list">
                <?php foreach ($config['items'] as $item): ?>
                <div class="item-row" data-name="<?= htmlspecialchars($item['name']) ?>" data-category="<?= htmlspecialchars($item['category']) ?>">
                    <div class="item-info">
                        <span class="item-name"><?= htmlspecialchars($item['name']) ?></span>
                        <span class="item-category"><?= htmlspecialchars($item['category']) ?></span>
                    </div>
                    <div class="item-actions">
                        <button type="button" class="edit-btn" onclick="editItem(this)">Edit</button>
                        <button type="button" class="delete-btn" onclick="deleteItem(this)">Delete</button>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
            <div class="modal-buttons">
                <button type="button" class="cancel-btn" onclick="closeModal()">Close</button>
            </div>
        </div>
    </div>
</div>

<!-- Edit Item Modal -->
<div class="modal" id="editItemModal">
    <div class="modal-content">
        <h2>Edit Item</h2>
        <form id="editItemForm">
            <input type="hidden" id="oldName">
            <div class="form-group">
                <label for="newName">Name:</label>
                <input type="text" id="newName" required>
            </div>
            <div class="form-group">
                <label for="newCategory">Category:</label>
                <input type="text" id="newCategory" required>
            </div>
            <div class="modal-buttons">
                <button type="button" class="cancel-btn" onclick="closeEditModal()">Cancel</button>
                <button type="submit" class="submit-btn">Save Changes</button>
            </div>
        </form>
    </div>
</div>
</body>
</html>
