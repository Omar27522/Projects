<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expenses Tracker</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css" type="text/css">
</head>
<body>
<?php
// Load configuration and expenses data
$config = json_decode(file_get_contents('config.json'), true);
$expenses = json_decode(file_get_contents('expenses.json'), true);

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

// Read and decode the JSON files
$jsonData = file_get_contents('expenses.json');
$configData = file_get_contents('config.json');
$data = json_decode($jsonData, true);
$config = json_decode($configData, true);

// Sort items alphabetically
usort($config['items'], function($a, $b) {
    return strcasecmp($a['name'], $b['name']);
});

echo "<h1>Expenses</h1>";

echo "<table>";
echo "<tr>";
echo "<th>Date</th>";
echo "<th>Item</th>";
echo "<th>Place</th>";
echo "<th>Amount</th>";
echo "<th>Type</th>";
echo "</tr>";

foreach ($data['expenses'] as $expense) {
    echo "<tr>";
    echo "<td>" . htmlspecialchars($expense['date']) . "</td>";
    echo "<td>" . htmlspecialchars($expense['item']) . "</td>";
    echo "<td>" . htmlspecialchars($expense['place']) . "</td>";
    echo "<td>" . htmlspecialchars($expense['amount']) . "</td>";
    echo "<td>" . htmlspecialchars($expense['type']) . "</td>";
    echo "</tr>";
}

echo "</table>";
?>
<button class="new-entry-btn" onclick="openModal()">New Entry</button>

<!-- Modal Form -->
<div class="modal" id="expenseModal">
    <div class="modal-content">
        <div class="modal-tabs">
            <button class="tab-btn active" onclick="switchTab('expense')">New Expense</button>
            <button class="tab-btn" onclick="switchTab('items')">Manage Items</button>
        </div>

        <!-- New Expense Tab -->
        <div id="expenseTab" class="tab-content active">
            <form id="expenseForm">
                <div class="form-steps">
                    <!-- Step 1: Date -->
                    <div class="form-step active" id="dateStep">
                        <div class="form-group full-container">
                            <label for="date">Date:</label>
                            <input type="text" id="date" name="date" required>
                            <div class="step-buttons">
                                <button type="button" class="cancel-btn" onclick="cancelExpense()">Cancel</button>
                                <button type="button" class="next-btn" onclick="nextStep('dateStep', 'itemStep')">Next</button>
                            </div>
                        </div>
                    </div>

                    <!-- Step 2: Item -->
                    <div class="form-step" id="itemStep">
                        <div class="form-group full-container">
                            <label for="item">Item:</label>
                            <div class="input-with-dropdown">
                                <input type="text" id="item" name="item" list="items" required autocomplete="off">
                                <datalist id="items">
                                    <?php
                                    foreach ($config['items'] as $item) {
                                        echo "<option value='" . htmlspecialchars($item['name']) . "' data-category='" . htmlspecialchars($item['category']) . "'>";
                                    }
                                    ?>
                                </datalist>
                            </div>
                            <div class="step-buttons">
                                <button type="button" class="cancel-btn" onclick="cancelExpense()">Cancel</button>
                                <button type="button" class="prev-btn" onclick="prevStep('itemStep', 'dateStep')">Back</button>
                                <button type="button" class="next-btn" onclick="nextStep('itemStep', 'placeStep')">Next</button>
                            </div>
                        </div>
                    </div>

                    <!-- Step 3: Place -->
                    <div class="form-step" id="placeStep">
                        <div class="form-group full-container">
                            <label for="place">Place:</label>
                            <input type="text" id="place" name="place" list="places" required autocomplete="off">
                            <datalist id="places">
                                <?php
                                foreach ($uniquePlaces as $place) {
                                    echo "<option value='" . htmlspecialchars($place) . "'>";
                                }
                                ?>
                            </datalist>
                            <div class="step-buttons">
                                <button type="button" class="cancel-btn" onclick="cancelExpense()">Cancel</button>
                                <button type="button" class="prev-btn" onclick="prevStep('placeStep', 'itemStep')">Back</button>
                                <button type="button" class="next-btn" onclick="nextStep('placeStep', 'amountStep')">Next</button>
                            </div>
                        </div>
                    </div>

                    <!-- Step 4: Amount -->
                    <div class="form-step" id="amountStep">
                        <div class="form-group full-container">
                            <label for="amount">Amount:</label>
                            <input type="number" id="amount" name="amount" step="0.01" required>
                            <div class="step-buttons">
                                <button type="button" class="cancel-btn" onclick="cancelExpense()">Cancel</button>
                                <button type="button" class="prev-btn" onclick="prevStep('amountStep', 'placeStep')">Back</button>
                                <button type="button" class="next-btn" onclick="nextStep('amountStep', 'typeStep')">Next</button>
                            </div>
                        </div>
                    </div>

                    <!-- Step 5: Type -->
                    <div class="form-step" id="typeStep">
                        <div class="form-group full-container">
                            <label for="type">Type:</label>
                            <input type="text" id="type" name="type" list="types" required autocomplete="off">
                            <datalist id="types">
                                <?php
                                foreach ($uniqueTypes as $type) {
                                    echo "<option value='" . htmlspecialchars($type) . "'>";
                                }
                                ?>
                            </datalist>
                            <div class="step-buttons">
                                <button type="button" class="cancel-btn" onclick="cancelExpense()">Cancel</button>
                                <button type="button" class="prev-btn" onclick="prevStep('typeStep', 'amountStep')">Back</button>
                                <button type="button" class="next-btn" onclick="showConfirmation()">Review</button>
                            </div>
                        </div>
                    </div>

                    <!-- Confirmation Step -->
                    <div class="form-step" id="confirmationStep">
                        <div class="confirmation-content">
                            <h3>Review Your Expense</h3>
                            <div class="confirmation-item">
                                <span class="label">Date:</span>
                                <span id="confirm-date"></span>
                            </div>
                            <div class="confirmation-item">
                                <span class="label">Item:</span>
                                <span id="confirm-item"></span>
                            </div>
                            <div class="confirmation-item">
                                <span class="label">Place:</span>
                                <span id="confirm-place"></span>
                            </div>
                            <div class="confirmation-item">
                                <span class="label">Amount:</span>
                                <span id="confirm-amount"></span>
                            </div>
                            <div class="confirmation-item">
                                <span class="label">Type:</span>
                                <span id="confirm-type"></span>
                            </div>
                            <div class="step-buttons">
                                <button type="button" class="cancel-btn" onclick="cancelExpense()">Cancel</button>
                                <button type="button" class="prev-btn" onclick="prevStep('confirmationStep', 'typeStep')">Edit</button>
                                <button type="submit" class="submit-btn">Submit</button>
                            </div>
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

<script>
// Store all data for autofill
let itemsData = <?php echo json_encode($config['items']); ?>;
let expensesData = <?php echo json_encode($expenses['expenses']); ?>;

// Initialize autofill data
document.addEventListener('DOMContentLoaded', function() {
    // Pre-fill today's date
    const today = new Date();
    document.getElementById('date').value = today.toISOString().split('T')[0];

    // Set up input event listeners
    setupAutofill('item', 'items');
    setupAutofill('place', 'places');
    setupAutofill('type', 'types');
});

function setupAutofill(inputId, datalistId) {
    const input = document.getElementById(inputId);
    const datalist = document.getElementById(datalistId);
    
    input.addEventListener('input', function(e) {
        const value = e.target.value.toLowerCase();
        
        // Clear existing options
        while (datalist.firstChild) {
            datalist.removeChild(datalist.firstChild);
        }
        
        // Add filtered options
        let options = [];
        if (inputId === 'item') {
            options = itemsData.map(item => item.name);
        } else if (inputId === 'place') {
            options = [...new Set(expensesData.map(expense => expense.place))];
        } else if (inputId === 'type') {
            options = [...new Set([
                ...itemsData.map(item => item.category),
                ...expensesData.map(expense => expense.type)
            ])];
        }
        
        options.filter(opt => opt.toLowerCase().includes(value))
              .forEach(opt => {
                  const option = document.createElement('option');
                  option.value = opt;
                  if (inputId === 'item') {
                      const itemData = itemsData.find(item => item.name === opt);
                      if (itemData) {
                          option.setAttribute('data-category', itemData.category);
                      }
                  }
                  datalist.appendChild(option);
              });
    });

    // Trigger initial population of datalist
    input.dispatchEvent(new Event('input'));
}

// Update type based on selected item
function updateType() {
    const itemInput = document.getElementById('item');
    const typeInput = document.getElementById('type');
    const selectedItem = itemInput.value;
    
    const itemData = itemsData.find(item => item.name.toLowerCase() === selectedItem.toLowerCase());
    if (itemData) {
        typeInput.value = itemData.category;
    }
}

// Add event listeners for form navigation
document.getElementById('item').addEventListener('change', updateType);
document.getElementById('item').addEventListener('input', function(e) {
    // Also try to update type while typing
    const itemData = itemsData.find(item => item.name.toLowerCase() === e.target.value.toLowerCase());
    if (itemData) {
        document.getElementById('type').value = itemData.category;
    }
});

function nextStep(currentId, nextId) {
    const currentInput = document.querySelector(`#${currentId} input`);
    if (currentInput && currentInput.value.trim() === '') {
        currentInput.focus();
        return;
    }
    
    document.getElementById(currentId).classList.remove('active');
    document.getElementById(nextId).classList.add('active');
    
    // Focus the input in the next step
    const nextInput = document.querySelector(`#${nextId} input`);
    if (nextInput) {
        nextInput.focus();
    }
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tab + 'Tab').classList.add('active');
}

function openModal() {
    document.getElementById('expenseModal').classList.add('show');
    
    // Get today's date in the format "DD-MMM"
    const today = new Date();
    const day = today.getDate();
    const month = today.toLocaleString('default', { month: 'short' });
    const formattedDate = `${day}-${month}`;
    
    // Pre-fill the date input
    document.getElementById('date').value = formattedDate;

    // Reset to expense tab
    switchTab('expense');
}

function closeModal() {
    document.getElementById('expenseModal').classList.remove('show');
    document.getElementById('expenseForm').reset();
}

function editItem(btn) {
    const item = btn.closest('.item-row');
    const modal = document.getElementById('editItemModal');
    document.getElementById('oldName').value = item.dataset.name;
    document.getElementById('newName').value = item.dataset.name;
    document.getElementById('newCategory').value = item.dataset.category;
    modal.classList.add('show');
}

function closeEditModal() {
    document.getElementById('editItemModal').classList.remove('show');
    document.getElementById('editItemForm').reset();
}

function deleteItem(btn) {
    if (!confirm('Are you sure you want to delete this item?')) return;
    
    const item = btn.closest('.item-row');
    const formData = new FormData();
    formData.append('action', 'delete');
    formData.append('name', item.dataset.name);
    
    fetch('manage_items.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            item.remove();
        } else {
            alert('Failed to delete item. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}

function prevStep(currentId, prevId) {
    document.getElementById(currentId).classList.remove('active');
    document.getElementById(prevId).classList.add('active');
}

function showConfirmation() {
    // Update confirmation values
    document.getElementById('confirm-date').textContent = document.getElementById('date').value;
    document.getElementById('confirm-item').textContent = document.getElementById('item').value;
    document.getElementById('confirm-place').textContent = document.getElementById('place').value;
    document.getElementById('confirm-amount').textContent = '$' + document.getElementById('amount').value;
    document.getElementById('confirm-type').textContent = document.getElementById('type').value;

    // Show confirmation step
    document.getElementById('typeStep').classList.remove('active');
    document.getElementById('confirmationStep').classList.add('active');
}

function cancelExpense() {
    // Reset the form
    document.getElementById('expenseForm').reset();
    
    // Reset to first step
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById('dateStep').classList.add('active');
    
    // Close the modal
    closeModal();
}

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

document.getElementById('expenseForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('add_expense.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            location.reload();
        } else {
            alert('Failed to add expense. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});

document.getElementById('editItemForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('action', 'edit');
    formData.append('oldName', document.getElementById('oldName').value);
    formData.append('newName', document.getElementById('newName').value);
    formData.append('category', document.getElementById('newCategory').value);
    
    fetch('manage_items.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeEditModal();
            location.reload();
        } else {
            alert('Failed to update item. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});
</script>
</body>
</html>
