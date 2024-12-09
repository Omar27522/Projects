<?php
function saveConfig($config) {
    return file_put_contents('config.json', json_encode($config, JSON_PRETTY_PRINT));
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $configData = file_get_contents('config.json');
    $config = json_decode($configData, true);
    
    if (isset($_POST['action'])) {
        header('Content-Type: application/json');
        
        switch ($_POST['action']) {
            case 'delete':
                if (isset($_POST['name'])) {
                    $config['items'] = array_filter($config['items'], function($item) {
                        return $item['name'] !== $_POST['name'];
                    });
                    if (saveConfig($config)) {
                        echo json_encode(['success' => true]);
                    } else {
                        http_response_code(500);
                        echo json_encode(['success' => false, 'message' => 'Failed to save']);
                    }
                }
                break;
                
            case 'edit':
                if (isset($_POST['oldName'], $_POST['newName'], $_POST['category'])) {
                    foreach ($config['items'] as &$item) {
                        if ($item['name'] === $_POST['oldName']) {
                            $item['name'] = $_POST['newName'];
                            $item['category'] = $_POST['category'];
                            break;
                        }
                    }
                    if (saveConfig($config)) {
                        echo json_encode(['success' => true]);
                    } else {
                        http_response_code(500);
                        echo json_encode(['success' => false, 'message' => 'Failed to save']);
                    }
                }
                break;
        }
        exit;
    }
}

// Read the config file
$configData = file_get_contents('config.json');
$config = json_decode($configData, true);

// Sort items alphabetically by name
usort($config['items'], function($a, $b) {
    return strcasecmp($a['name'], $b['name']);
});
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Items - Expenses Tracker</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css" type="text/css">
</head>
<body>
    <div class="container">
        <h1>Manage Items</h1>
        <a href="index.php" class="back-btn">← Back to Expenses</a>
        
        <div class="items-list">
            <?php foreach ($config['items'] as $item): ?>
            <div class="item-row" data-name="<?= htmlspecialchars($item['name']) ?>" data-category="<?= htmlspecialchars($item['category']) ?>">
                <div class="item-info">
                    <span class="item-name"><?= htmlspecialchars($item['name']) ?></span>
                    <span class="item-category"><?= htmlspecialchars($item['category']) ?></span>
                </div>
                <div class="item-actions">
                    <button class="edit-btn" onclick="editItem(this)">Edit</button>
                    <button class="delete-btn" onclick="deleteItem(this)">Delete</button>
                </div>
            </div>
            <?php endforeach; ?>
        </div>
    </div>

    <!-- Edit Modal -->
    <div class="modal" id="editModal">
        <div class="modal-content">
            <h2>Edit Item</h2>
            <form id="editForm">
                <input type="hidden" id="oldName">
                <div class="form-group">
                    <label for="newName">Name:</label>
                    <input type="text" id="newName" required>
                </div>
                <div class="form-group">
                    <label for="category">Category:</label>
                    <input type="text" id="category" required>
                </div>
                <div class="modal-buttons">
                    <button type="button" class="cancel-btn" onclick="closeEditModal()">Cancel</button>
                    <button type="submit" class="submit-btn">Save Changes</button>
                </div>
            </form>
        </div>
    </div>

    <script>
    function editItem(btn) {
        const item = btn.closest('.item-row');
        const modal = document.getElementById('editModal');
        document.getElementById('oldName').value = item.dataset.name;
        document.getElementById('newName').value = item.dataset.name;
        document.getElementById('category').value = item.dataset.category;
        modal.classList.add('show');
    }

    function closeEditModal() {
        document.getElementById('editModal').classList.remove('show');
        document.getElementById('editForm').reset();
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

    document.getElementById('editForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('action', 'edit');
        formData.append('oldName', document.getElementById('oldName').value);
        formData.append('newName', document.getElementById('newName').value);
        formData.append('category', document.getElementById('category').value);
        
        fetch('manage_items.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
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
