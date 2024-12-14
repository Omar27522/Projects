<?php
require_once 'db_connect.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $db = new Database();
    $response = ['success' => false, 'message' => ''];

    if (isset($_POST['delete_id'])) {
        try {
            $db->deleteGasEntry($_POST['delete_id']);
            $response['success'] = true;
            $response['message'] = 'Entry deleted successfully';
        } catch (Exception $e) {
            $response['message'] = "Error: " . $e->getMessage();
        }
        echo json_encode($response);
        exit();
    } elseif (isset($_POST['action']) && $_POST['action'] === 'filter') {
        $year = isset($_POST['filter_year']) ? $_POST['filter_year'] : null;
        $month = isset($_POST['filter_month']) ? $_POST['filter_month'] : null;
        
        $entries = $db->getFilteredEntries($year, $month);
        
        if ($entries !== false) {
            echo json_encode(['success' => true, 'entries' => $entries]);
        } else {
            echo json_encode(['success' => false, 'message' => 'Error filtering entries']);
        }
        exit;
    } else {
        $date = $_POST['date'];
        $station = $_POST['station'];
        $type = $_POST['type'];
        $amount = $_POST['amount'];
        $gallons = $_POST['gallons'];
        $ppg = $_POST['ppg'];

        if (isset($_POST['entry_id']) && !empty($_POST['entry_id'])) {
            // Update existing entry
            $success = $db->updateGasEntry($_POST['entry_id'], $date, $station, $type, $amount, $gallons, $ppg);
            $message = $success ? 'Entry updated successfully' : 'Error updating entry';
        } else {
            // Add new entry
            $success = $db->addGasEntry($date, $station, $type, $amount, $gallons, $ppg);
            $message = $success ? 'Entry added successfully' : 'Error adding entry';
        }

        $response = [
            'success' => $success,
            'message' => $message,
            'entries' => $db->getAllGasEntries()
        ];
        
        echo json_encode($response);
        exit();
    }
}

// If it's not a POST request, show the regular page
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="gas.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="table_sort.js" defer></script>
    <script src="gas.js" defer></script>
    <title>GAS</title>
</head>

<body>
    <h1>Add New Gas Entry</h1>

    <!-- Add new entry form -->

    <form id="gasForm" method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>">
        <input type="hidden" id="entry_id" name="entry_id" value="">
        <div class="form-group">
            <label for="date">Date:</label>
            <input type="text" id="date" name="date" value="<?php echo date('M j'); ?>" required>
        </div>
        <div class="form-group">
            <label for="station">Station:</label>
            <select id="station" name="station"
                onchange="if(this.value=='other') document.getElementById('newStationDiv').style.display='block'; else document.getElementById('newStationDiv').style.display='none';">
                <option value="">Select Station</option>
                <option value="Pemex">Pemex</option>
                <option value="Shell">Shell</option>
                <option value="Chevron">Chevron</option>
                <option value="Arco">Arco</option>
                <option value="Costco">Costco</option>
                <option value="76">76</option>
                <option value="other">Add New Station...</option>
            </select>
            <button type="button" onclick="removeStation()"
                style="margin-left: 5px; transform: translateY(-1px); padding: 2px 6px; background: none; border: none; cursor: pointer;">
                <i class="fas fa-trash-alt" style="color: #666; font-size: 14px;"></i>
            </button>
            <hr>
            <div id="newStationDiv"
                style="display:none; margin-top: 10px;margin-bottom:0px; transform: translateY(70px) translateX(-220px);">
                <input type="text" id="newStation" name="newStation" placeholder="Enter new station name">
                <button type="button" onclick="addNewStation()"
                    style="transform: translateY(-13px) translateX(-2px);float: right;">Add</button>
            </div>
        </div>
        <div class="form-group">
            <label for="type">Type:</label>
            <select id="type" name="type" required>
                <option value="">Select Type</option>
                <option value="89 Regular">89 Regular</option>
                <option value="90 Plus">90 Plus</option>
                <option value="91 Premium">91 Premium</option>
            </select>
        </div>
        <div class="form-group">
            <label for="amount">Amount ($):</label>
            <input type="number" id="amount" name="amount" step="0.01" required oninput="calculatePPG()">
        </div>
        <div class="form-group">
            <label for="gallons">Gallons:</label>
            <input type="number" id="gallons" name="gallons" step="0.001" required oninput="calculatePPG()">
        </div>
        <div class="form-group">
            <label for="ppg">Price/Gallon:</label>
            <input type="number" id="ppg" name="ppg" step="0.001" readonly style="background-color: #f0f0f0;">
        </div>
        <button type="submit">Add Entry</button>
    </form>

    <details>
        <summary>Filter Entries</summary>
        <form id="filterForm" class="filter-form">
        <select id="yearFilter" name="year">
            <option value="">Select Year</option>
            <?php
            $currentYear = date('Y');
            for($y = $currentYear - 1; $y <= $currentYear + 1; $y++) {
                echo "<option value='$y'>$y</option>";
            }
            ?>
        </select>
        <select id="monthFilter" name="month">
            <option value="">Select Month</option>
            <?php
            $months = [
                1 => 'January', 2 => 'February', 3 => 'March', 
                4 => 'April', 5 => 'May', 6 => 'June',
                7 => 'July', 8 => 'August', 9 => 'September',
                10 => 'October', 11 => 'November', 12 => 'December'
            ];
            foreach($months as $num => $name) {
                echo "<option value='$num'>$name</option>";
            }
            ?>
        </select>
        <button type="button" id="applyFilter">Apply Filter</button>
        <button type="button" id="resetFilter">Reset</button>
    </form>
    </details>
    <!-- Display existing entries -->
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Station</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Gallons</th>
                <th>P / G</th>
            </tr>
        </thead>
        <tbody>
            <?php
            $db = new Database();
            $entries = $db->getAllGasEntries();
            foreach ($entries as $entry) {
                echo "<tr onclick='showEntry(" . json_encode($entry) . ")'>";
                echo "<td>{$entry['date']}</td>";
                echo "<td>{$entry['station']}</td>";
                echo "<td>{$entry['type']}</td>";
                echo "<td>{$entry['amount']}</td>";
                echo "<td>{$entry['gallons']}</td>";
                echo "<td>{$entry['price_per_gallon']}</td>";
                echo "</tr>";
            }
            ?>
        </tbody>
    </table>

    <!-- Modal for viewing/editing entry -->
    <div id="entryModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2>Gas Entry Details</h2>
            <div id="entryDetails">
                <p><strong>Date:</strong> <span id="modalDate"></span></p>
                <p><strong>Station:</strong> <span id="modalStation"></span></p>
                <p><strong>Type:</strong> <span id="modalType"></span></p>
                <p><strong>Amount:</strong> $<span id="modalAmount"></span></p>
                <p><strong>Gallons:</strong> <span id="modalGallons"></span></p>
                <p><strong>Price per Gallon:</strong> $<span id="modalPPG"></span></p>
            </div>
            <div class="modal-buttons">
                <button class="btn-edit" onclick="editEntry()">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn-delete" onclick="deleteEntry()">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        </div>
    </div>
    <fieldset id="tanksPerMonth" style="">
        <legend>Tanks of Gas Per Month</legend>
        <aside style="float: right;">
            <select style=" width: auto;height: 30px; margin: 0; padding: 0;">
                <option>Month</option>
                <option>January</option>
                <option>February</option>
                <option>March</option>
                <option>April</option>
                <option>May</option>
                <option>June</option>
                <option>July</option>
                <option>August</option>
                <option>September</option>
                <option>October</option>
                <option>November</option>
                <option>December</option>
            </select>
        </aside>
        <h2 style="margin-top: 3%;">
            <input type="number" id="gallonsPerMonth" value="18" min="0" step="0.25" style="width: 30px; height: 30px; padding: 5px;"> Gallons
            <small><input type="number" id="milesPerTank" value="370" min="0" step="5.00" style="width: 40px; height: 30px; padding: 5px;"> Miles per Tank</small>
        </h2>
        <p>
            Gas this month:<br />
            <span style="padding-left: 200px;"><span id="gasPerMonth">0.000</span> Gallons</span>
        </p>
        <p>
            Total Amount this month:<br />
            <span style="padding-left: 200px;"><span id="dollarsPerMonth">$0.00</span></span>
        </p>
        <p>
            Average Price per Gallon:<br />
            <span style="padding-left: 200px;"><span id="avgPricePerGallon">$0.00</span></span>
        </p>
        <p>
            Miles Traveled this month:<br />
            <span style="padding-left: 200px;"><span id="milesTraveled">0</span> Miles Traveled</span>
        </p>
        </fieldset>
    <table>
        <thead>Total Milles Driven</thead>
        <tbody>
            <tr>
                <td>Total Miles Driven:</td>
                <td id="totalMiles">80</td>
            </tr>
            <tr>
                <td>First of the month:</td>
                <td id="first_of_the_month">80</td>
            </tr>
            <tr>
                <td>Last of the month:</td>
                <td id="first_of_the_month">80</td>
            </tr>
            <tr>
                <td>Monthly Miles:</td>
                <td id="monthly_miles">=first-last</td>
            </tr>
        </tbody>
    </table>
    <hr class="divider">
    <?php footer();?>
</body>

</html>