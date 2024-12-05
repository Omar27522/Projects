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
        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            min-width: 800px;
            
        }

        .table-container {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 1em;
            display: flex;
            justify-content: center;
        }

        th, td {
            padding: 8px;
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        th {
            background-color: #black;
            position: sticky;
            top: 0;
            z-index: 1;
        }

        /* Column widths */
        th:nth-child(1), td:nth-child(1) { width: 15%; } /* Date */
        th:nth-child(2), td:nth-child(2) { width: 25%; } /* Item */
        th:nth-child(3), td:nth-child(3) { width: 20%; } /* Place */
        th:nth-child(4), td:nth-child(4) { width: 15%; } /* Amount */
        th:nth-child(5), td:nth-child(5) { width: 15%; } /* Type */
        th:nth-child(6), td:nth-child(6) { width: 10%; } /* Actions */

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
            transition: transform 0.1s ease;
        }

        .action-buttons button:hover {
            transform: scale(1.2);
        }

        .edit-btn i {
            color: #28a745;
        }

        .delete-btn i {
            color: #dc3545;
        }

        .edit-mode input {
            width: 100%;
            padding: 4px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: inherit;
            font-family: inherit;
        }

        .edit-mode .action-buttons {
            display: flex;
            gap: 4px;
        }

        .save-btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
        }

        .cancel-btn {
            background-color: #f44336;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
        }

        @media screen and (max-width: 768px) {
            table {
                font-size: 0.9em;
            }
            
            th, td {
                padding: 6px;
            }
        }
    </style>
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

echo "<div class='table-container'>";
echo "<table>";
echo "<tr>";
echo "<th>Date</th>";
echo "<th>Item</th>";
echo "<th>Place</th>";
echo "<th>Amount</th>";
echo "<th>Type</th>";
echo "<th>Actions</th>";
echo "</tr>";

echo "<tbody>";
if (empty($data['expenses'])) {
    echo '<tr class="empty-row">';
    echo '<td colspan="6" style="text-align: center; padding: 20px; color: #666;">';
    echo 'No expenses found. Click the "Add Expense" button to add one.';
    echo '</td>';
    echo '</tr>';
} else {
    foreach ($data['expenses'] as $index => $expense): ?>
        <tr>
            <td><?= htmlspecialchars($expense['date']) ?></td>
            <td><?= htmlspecialchars($expense['item']) ?></td>
            <td><?= htmlspecialchars($expense['place']) ?></td>
            <td><?= htmlspecialchars($expense['amount']) ?></td>
            <td><?= htmlspecialchars($expense['type']) ?></td>
            <td>
                <div class="action-buttons">
                    <button onclick="editExpense(this)" class="edit-btn" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="deleteExpense(this)" class="delete-btn" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    <?php endforeach; ?>
<?php }
echo "</tbody>";
echo "</table>";
echo "</div>";
?>
<button class="new-entry-btn" onclick="openModal()">
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

    // Add keypress event listener for the review step
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const reviewStep = document.getElementById('reviewStep');
            if (reviewStep && reviewStep.classList.contains('active')) {
                e.preventDefault();
                submitExpense();
            } else {
                // For other steps, trigger the next button click
                const currentStep = document.querySelector('.form-step.active');
                if (currentStep) {
                    const nextBtn = currentStep.querySelector('.next-btn');
                    if (nextBtn) {
                        e.preventDefault();
                        nextBtn.click();
                    }
                }
            }
        }
    });
    
    // Add event listeners for next buttons
    document.querySelectorAll('.next-btn').forEach(button => {
        button.addEventListener('click', () => {
            const currentStep = button.closest('.form-step');
            const nextStep = currentStep.nextElementSibling;
            
            if (nextStep) {
                currentStep.classList.remove('active');
                nextStep.classList.add('active');
                updateReviewStep();
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
    document.getElementById(currentId).classList.remove('active');
    document.getElementById(nextId).classList.add('active');
}

function showConfirmation() {
    // Update confirmation values
    document.getElementById('reviewDate').textContent = document.getElementById('date').value;
    document.getElementById('reviewItem').textContent = document.getElementById('item').value;
    document.getElementById('reviewPlace').textContent = document.getElementById('place').value;
    document.getElementById('reviewAmount').textContent = document.getElementById('amount').value;
    document.getElementById('reviewType').textContent = document.getElementById('type').value;

    // Show confirmation step
    document.getElementById('typeStep').classList.remove('active');
    document.getElementById('reviewStep').classList.add('active');
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

function submitExpense() {
    const formData = new FormData(document.getElementById('expenseForm'));
    
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
}

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
}

function editExpense(button) {
    const row = button.closest('tr');
    const cells = row.cells;
    const index = Array.from(row.parentElement.children).indexOf(row);
    
    // Store original values
    const originalValues = {
        date: cells[0].textContent,
        item: cells[1].textContent,
        place: cells[2].textContent,
        amount: cells[3].textContent.replace('$', ''),
        type: cells[4].textContent
    };
    
    // Add edit-mode class to row
    row.classList.add('edit-mode');
    
    // Replace cell contents with input fields
    cells[0].innerHTML = `<input type="text" value="${originalValues.date}" placeholder="DD-MMM">`;
    cells[1].innerHTML = `<input type="text" value="${originalValues.item}">`;
    cells[2].innerHTML = `<input type="text" value="${originalValues.place}">`;
    cells[3].innerHTML = `<input type="text" value="${originalValues.amount}" placeholder="Enter amount">`;
    cells[4].innerHTML = `<input type="text" value="${originalValues.type}">`;
    cells[5].innerHTML = `
        <div class="action-buttons">
            <button onclick="saveEdit(this)" class="save-btn" title="Save">
                <i class="fas fa-check"></i>
            </button>
            <button onclick="cancelEdit(this, ${JSON.stringify(originalValues)})" class="cancel-btn" title="Cancel">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

function saveEdit(button) {
    const row = button.closest('tr');
    const cells = row.cells;
    const index = Array.from(row.parentElement.children).indexOf(row);
    
    const updatedExpense = {
        date: cells[0].querySelector('input').value,
        item: cells[1].querySelector('input').value,
        place: cells[2].querySelector('input').value,
        amount: cells[3].querySelector('input').value,
        type: cells[4].querySelector('input').value
    };
    
    fetch('edit_expense.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `index=${index}&date=${updatedExpense.date}&item=${updatedExpense.item}&place=${updatedExpense.place}&amount=${updatedExpense.amount}&type=${updatedExpense.type}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the row with new values
            cells[0].textContent = updatedExpense.date;
            cells[1].textContent = updatedExpense.item;
            cells[2].textContent = updatedExpense.place;
            cells[3].textContent = '$' + updatedExpense.amount;
            cells[4].textContent = updatedExpense.type;
            cells[5].innerHTML = `
                <div class="action-buttons">
                    <button onclick="editExpense(this)" class="edit-btn" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="deleteExpense(this)" class="delete-btn" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            // Remove edit-mode class
            row.classList.remove('edit-mode');
        } else {
            alert('Failed to save changes: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to save changes');
    });
}

function deleteExpense(button) {
    const row = button.closest('tr');
    const index = Array.from(row.parentElement.children).indexOf(row);
    
    if (confirm('Are you sure you want to delete this expense?')) {
        fetch('delete_expense.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'index=' + index
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                row.remove();
                // Check if this was the last row
                const tbody = document.querySelector('tbody');
                if (tbody.children.length === 0) {
                    tbody.innerHTML = `
                        <tr class="empty-row">
                            <td colspan="6" style="text-align: center; padding: 20px; color: #666;">
                                No expenses found. Click the "Add Expense" button to add one.
                            </td>
                        </tr>
                    `;
                }
            } else {
                alert('Failed to delete expense: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to delete expense');
        });
    }
}

function cancelEdit(button, originalValues) {
    const row = button.closest('tr');
    const cells = row.cells;
    
    // Restore original values
    cells[0].textContent = originalValues.date;
    cells[1].textContent = originalValues.item;
    cells[2].textContent = originalValues.place;
    cells[3].textContent = '$' + originalValues.amount;
    cells[4].textContent = originalValues.type;
    cells[5].innerHTML = `
        <div class="action-buttons">
            <button onclick="editExpense(this)" class="edit-btn" title="Edit">
                <i class="fas fa-edit"></i>
            </button>
            <button onclick="deleteExpense(this)" class="delete-btn" title="Delete">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    // Remove edit-mode class
    row.classList.remove('edit-mode');
}

function prevStep(currentId, prevId) {
    document.getElementById(currentId).classList.remove('active');
    document.getElementById(prevId).classList.add('active');
}

function switchTab(tab) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add active class to selected tab and content
    const selectedTab = document.querySelector(`.tab-btn[onclick="switchTab('${tab}')"]`);
    const selectedContent = document.getElementById(tab + 'Tab');
    
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    if (selectedContent) {
        selectedContent.classList.add('active');
    }
}

function openModal() {
    const modal = document.getElementById('expenseModal');
    if (modal) {
        modal.classList.add('show');
        
        // Reset form and show first step
        const form = document.getElementById('expenseForm');
        if (form) {
            form.reset();
        }
        
        // Reset steps
        document.querySelectorAll('.form-step').forEach(step => step.classList.remove('active'));
        const dateStep = document.getElementById('dateStep');
        if (dateStep) {
            dateStep.classList.add('active');
        }
        
        // Set today's date
        const today = new Date();
        const day = today.getDate();
        const month = today.toLocaleString('default', { month: 'short' });
        const dateInput = document.getElementById('date');
        if (dateInput) {
            dateInput.value = `${day}-${month}`;
        }
        
        // Reset to expense tab
        switchTab('expense');
    }
}

function closeModal() {
    const modal = document.getElementById('expenseModal');
    if (modal) {
        modal.classList.remove('show');
    }
}

// Add click event listener for the new entry button
document.addEventListener('DOMContentLoaded', function() {
    const newEntryBtn = document.querySelector('.new-entry-btn');
    if (newEntryBtn) {
        newEntryBtn.addEventListener('click', openModal);
    }
});

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
</script>
</body>
</html>
