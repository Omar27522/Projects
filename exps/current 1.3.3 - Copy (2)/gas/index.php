<?php
require_once '../db_connect.php';
$db = new Database();

// Handle station management
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['new_station'])) {
        $newStation = trim($_POST['new_station']);
        if (!empty($newStation)) {
            if ($db->addStation($newStation)) {
                header('Location: index.php?message=Station added successfully&type=success');
                exit();
            }
        }
    } elseif (isset($_POST['delete_station'])) {
        $stationToDelete = $_POST['delete_station'];
        if ($db->deleteStation($stationToDelete)) {
            header('Location: index.php?message=Station deleted successfully&type=success');
            exit();
        }
    } else {
        // Existing gas entry handling code
        $date = $_POST['date'];
        $station = $_POST['station'];
        $type = $_POST['type'];
        $amount = floatval($_POST['amount']);
        $gallons = floatval($_POST['gallons']);
        $price_per_gallon = $gallons > 0 ? $amount / $gallons : 0;
        if ($db->addGasEntry($date, $station, $type, $amount, $gallons, $price_per_gallon)) {
            $message = "Entry added successfully!";
        }
    }
}

// Get all gas entries and stations
$gasEntries = $db->getAllGasEntries();
$stations = $db->getAllStations();
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gas Entry</title>
    <link rel="stylesheet" href="../gas/gas.css">
    <link rel="stylesheet" href="../style.css">
</head>

<body>
    <div class="links">
        <h1>Gas Entry</h1>
        <?php links(); ?>
    </div>

    <?php if (isset($_GET['message'])): ?>
    <div class="message <?php echo isset($_GET['type']) ? htmlspecialchars($_GET['type']) : ''; ?>" id="statusMessage">
        <?php echo htmlspecialchars($_GET['message']); ?>
    </div>
    <?php endif; ?>

    <?php if (isset($message)): ?>
    <div class="message success" id="successMessage"><?php echo htmlspecialchars($message); ?></div>
    <?php endif; ?>

    <?php if (isset($error)): ?>
    <div class="message error"><?php echo htmlspecialchars($error); ?></div>
    <?php endif; ?>

    <form method="POST" action="" class="gas-form">
        <div class="field">
            <label for="date">Date</label>
            <input type="text" id="date" name="date"
                value="<?php date_default_timezone_set('America/Los_Angeles'); echo date('M-j g:i A'); ?>" required>
        </div>

        <div class="field">
            <label for="station">Station</label>
            <select id="station" name="station" required>
                <?php foreach ($stations as $station): ?>
                <option value="<?php echo htmlspecialchars($station); ?>"><?php echo htmlspecialchars($station); ?>
                </option>
                <?php endforeach; ?>
            </select>
            <button type="button" onclick="toggleStationManagement()" class="manage-stations-btn">Manage
                Stations</button>
        </div>

        <div class="field">
            <label for="type">Fuel Type</label>
            <select id="type" name="type" required>
                <option value="Regular">Regular</option>
                <option value="Plus">Plus</option>
                <option value="Premium">Premium</option>
            </select>
        </div>

        <div class="field">
            <label for="amount">Total Amount ($)</label>
            <input type="number" id="amount" name="amount" step="0.01" required oninput="calculatePPG()">

            <label for="gallons">Gallons</label>
            <input type="number" id="gallons" name="gallons" step="0.001" required oninput="calculatePPG()">
        </div>

        <div id="ppgDisplay" class="calculated">
            Price per gallon: $0.00
        </div>

        <input type="submit" value="Add Gas Entry">
    </form>

    <!-- Station Management Dialog -->
    <div id="stationManagement" class="station-management" style="display: none;">
        <div class="station-form">
            <form id="addStationForm" class="add-station-form">
                <input type="text" name="station_name" placeholder="New station name" required>
                <button type="submit">Add Station</button>
            </form>
            <div class="station-list" id="stationList">
                <?php foreach ($stations as $station): ?>
                <div class="station-item">
                    <?php echo htmlspecialchars($station); ?>
                    <button onclick="deleteStation('<?php echo htmlspecialchars($station); ?>')"
                        class="delete-station-btn">×</button>
                </div>
                <?php endforeach; ?>
            </div>
        </div>
    </div>

    <script>
    // Auto-hide messages
    document.addEventListener('DOMContentLoaded', function() {
        const messages = ['successMessage', 'statusMessage'];
        messages.forEach(function(id) {
            const messageElement = document.getElementById(id);
            if (messageElement && messageElement.classList.contains('success')) {
                setTimeout(function() {
                    messageElement.style.transition = 'opacity 0.5s';
                    messageElement.style.opacity = '0';
                    setTimeout(function() {
                        messageElement.style.display = 'none';
                    }, 500);
                }, 2000);
            }
        });

        // Add station form submission
        document.getElementById('addStationForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData();
            formData.append('action', 'add');
            formData.append('station_name', this.station_name.value);

            fetch('../gas/manage_stations.php', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Server response:', data);
                    if (data.success) {
                        updateStationsList(data.stations);
                        this.reset();
                        showMessage(data.message, 'success');
                    } else {
                        showMessage(data.message || 'Error adding station', 'error');
                        console.error('Server error:', data);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('Error communicating with server. Check console for details.',
                        'error');
                });
        });
    });

    function deleteStation(stationName) {
        if (confirm('Are you sure you want to delete this station?')) {
            const formData = new FormData();
            formData.append('action', 'delete');
            formData.append('station_name', stationName);

            fetch('../gas/manage_stations.php', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateStationsList(data.stations);
                        showMessage(data.message, 'success');
                    } else {
                        showMessage(data.message || 'Error deleting station', 'error');
                    }
                });
        }
    }

    function updateStationsList(stations) {
        // Update the stations dropdown
        const dropdown = document.getElementById('station');
        dropdown.innerHTML = stations.map(station =>
            `<option value="${station}">${station}</option>`
        ).join('');

        // Update the station list in the management dialog
        const stationList = document.getElementById('stationList');
        stationList.innerHTML = stations.map(station => `
            <div class="station-item">
                ${station}
                <button onclick="deleteStation('${station}')" class="delete-station-btn">×</button>
            </div>
        `).join('');
    }

    function showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;

        // Insert message at the top of the form
        const form = document.querySelector('.gas-form');
        form.insertBefore(messageDiv, form.firstChild);

        // Auto-hide message
        setTimeout(() => {
            messageDiv.style.transition = 'opacity 0.5s';
            messageDiv.style.opacity = '0';
            setTimeout(() => messageDiv.remove(), 500);
        }, 2000);
    }

    function calculatePPG() {
        const amount = parseFloat(document.getElementById('amount').value) || 0;
        const gallons = parseFloat(document.getElementById('gallons').value) || 0;
        const ppg = gallons > 0 ? (amount / gallons).toFixed(2) : '0.00';
        document.getElementById('ppgDisplay').textContent = `Price per gallon: $${ppg}`;
    }

    function toggleStationManagement() {
        const dialog = document.getElementById('stationManagement');
        dialog.style.display = dialog.style.display === 'none' ? 'block' : 'none';
    }

    // Close dialog when clicking outside
    document.addEventListener('click', function(event) {
        const dialog = document.getElementById('stationManagement');
        const manageBtn = document.querySelector('.manage-stations-btn');
        if (!dialog.contains(event.target) && !manageBtn.contains(event.target) && dialog.style.display ===
            'block') {
            dialog.style.display = 'none';
        }
    });
    </script>

    <div class="table-container" style="overflow-y: auto; max-height: 500px;">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Station</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Gallons</th>
                    <th>Price/Gallon</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php if ($gasEntries): ?>
                <?php foreach ($gasEntries as $entry): ?>
                <tr>
                    <td data-label="Date"><?php echo htmlspecialchars($entry['date'] ?? ''); ?></td>
                    <td data-label="Station"><?php echo htmlspecialchars($entry['station'] ?? ''); ?></td>
                    <td data-label="Type"><?php echo htmlspecialchars($entry['type'] ?? ''); ?></td>
                    <td data-label="Amount">$<?php echo number_format($entry['amount'] ?? 0, 2); ?></td>
                    <td data-label="Gallons"><?php echo number_format($entry['gallons'] ?? 0, 3); ?></td>
                    <td data-label="Price/Gallon">$<?php echo number_format($entry['price_per_gallon'] ?? 0, 3); ?></td>
                    <td data-label="Actions" class="actions">
                        <button onclick="editEntry(<?php echo $entry['id']; ?>)" class="edit-btn">Edit</button>
                        <button onclick="deleteEntry(<?php echo $entry['id']; ?>)" class="delete-btn">Delete</button>
                    </td>
                </tr>
                <?php endforeach; ?>
                <?php else: ?>
                <tr>
                    <td colspan="7" style="text-align: center;">No gas entries found</td>
                </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
    <div class="table-container" style="overflow-y: auto; max-height: 500px;background-color: transparent;">
        <?php
        require_once 'process_mileage.php';
        $latest_data = getLatestMileageData();
        $current_total = $latest_data ? $latest_data['cumulative_total'] : 48474; // Use default if no data
        ?>
IM alsmost there, first_miles has to stay when updated, and has to wait for last to be update so they can both clear and total miles can changer to new value 


||| IDK how to make this work |||
        <div id="mileageMessage" class="message" style="display: none;"></div>
        <form id="mileageForm">
            <h2 style="text-align: center; display: inline;margin: 0;padding: 0;">Total Miles</h2>
            <table class="data-table table-container" style="width: fit-content;" id="totalMiles">
                <tr>
                    <th><?php echo date('F Y'); ?></th>
                    <th style="width: fit-content;">Miles</th>
                    <th style="width: fit-content;">Last Month Total</th>
                </tr>
                <tr>
                    <td>First</td>
                    <td><input type="number" name="first_miles" id="first_miles" step="0.1" required></td>
                    <td><input style="width: 50%;" type="number" name="first_total" id="first_total" 
                        value="<?php echo htmlspecialchars($current_total); ?>" readonly></td>
                </tr>
                <tr>
                    <td>Last</td>
                    <td><input type="number" name="last_miles" id="last_miles" step="0.1"></td>
                    <td><button type="button" onclick="submitMileage()" class="submit-btn">Update Total</button></td>
                </tr>
            </table>
        </form>
    </div>

    <script>
    function deleteEntry(id) {
        if (confirm('Are you sure you want to delete this entry?')) {
            window.location.href = '../gas/delete_gas.php?id=' + id;
        }
    }

    function editEntry(id) {
        window.location.href = '../gas/edit_gas.php?id=' + id;
    }

    function showMileageMessage(message, type) {
        const messageDiv = document.getElementById('mileageMessage');
        messageDiv.textContent = message;
        messageDiv.className = `message ${type}`;
        messageDiv.style.display = 'block';
        
        // Scroll the message into view
        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }

    function submitMileage() {
        const firstMiles = parseFloat(document.getElementById('first_miles').value);
        const lastMiles = parseFloat(document.getElementById('last_miles').value);
        const firstTotal = parseFloat(document.getElementById('first_total').value);

        if (!firstMiles) {
            showMileageMessage('Please enter first miles reading', 'error');
            return;
        }

        if (lastMiles && lastMiles < firstMiles) {
            showMileageMessage('Last miles cannot be less than first miles', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('first_miles', firstMiles);
        formData.append('last_miles', lastMiles || '');
        formData.append('first_total', firstTotal);

        fetch('/gas/process_mileage.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (!lastMiles) {
                    // For first miles entry, just save the value and show message
                    document.getElementById('first_miles').value = firstMiles;
                    document.getElementById('first_miles').readOnly = true;
                    showMileageMessage('First miles reading saved. Enter last miles at end of month.', 'success');
                } else {
                    // For last miles entry, update total and reset fields
                    document.getElementById('first_total').value = data.new_total;
                    document.getElementById('first_miles').value = '';
                    document.getElementById('first_miles').readOnly = false;
                    document.getElementById('last_miles').value = '';
                    
                    showMileageMessage(`Miles updated! You drove ${data.monthly_total.toFixed(1)} miles this month. New total: ${data.new_total.toFixed(1)}`, 'success');
                }
            } else {
                showMileageMessage(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMileageMessage('Error saving mileage data', 'error');
        });
    }
    </script>

    <div class="table-container" style="overflow-y: auto; max-height: 500px;">
        <?php footer(); ?>
    </div>
</body>

</html>