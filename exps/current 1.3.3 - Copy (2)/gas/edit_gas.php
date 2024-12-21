<?php
require_once '../db_connect.php';
$db = new Database();

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['id'])) {
    $id = $_POST['id'];
    $date = $_POST['date'];
    $station = $_POST['station'];
    $type = $_POST['type'];
    $amount = floatval($_POST['amount']);
    $gallons = floatval($_POST['gallons']);
    $price_per_gallon = $gallons > 0 ? $amount / $gallons : 0;

    if ($db->updateGasEntry($id, $date, $station, $type, $amount, $gallons, $price_per_gallon)) {
        header('Location: index.php?message=Entry updated successfully&type=success');
    } else {
        header('Location: index.php?message=Error updating entry&type=error');
    }
    exit();
}

$entry = null;
if (isset($_GET['id'])) {
    $entry = $db->getGasEntryById($_GET['id']);
}

if (!$entry) {
    header('Location: index.php?message=Entry not found&type=error');
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Gas Entry</title>
    <link rel="stylesheet" href="gas.css">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <div class="links">
        <h1>Edit Gas Entry</h1>
        <?php links(); ?>
    </div>

    <form method="POST" action="" class="gas-form">
        <input type="hidden" name="id" value="<?php echo htmlspecialchars($entry['id']); ?>">
        
        <div class="field">
            <label for="date">Date</label>
            <input type="text" id="date" name="date" value="<?php echo htmlspecialchars($entry['date']); ?>" required>
        </div>

        <div class="field">
            <label for="station">Station</label>
            <select id="station" name="station" required>
                <option value="Shell" <?php echo $entry['station'] === 'Shell' ? 'selected' : ''; ?>>Shell</option>
                <option value="BP" <?php echo $entry['station'] === 'BP' ? 'selected' : ''; ?>>BP</option>
                <option value="Chevron" <?php echo $entry['station'] === 'Chevron' ? 'selected' : ''; ?>>Chevron</option>
            </select>
        </div>

        <div class="field">
            <label for="type">Type</label>
            <select id="type" name="type" required>
                <option value="Regular" <?php echo $entry['type'] === 'Regular' ? 'selected' : ''; ?>>Regular</option>
                <option value="Premium" <?php echo $entry['type'] === 'Premium' ? 'selected' : ''; ?>>Premium</option>
            </select>
        </div>

        <div class="field">
            <label for="amount">Total Amount ($)</label>
            <input type="number" id="amount" name="amount" step="0.01" required 
                   value="<?php echo htmlspecialchars($entry['amount']); ?>"
                   oninput="calculatePPG()">
        
            <label for="gallons">Gallons</label>
            <input type="number" id="gallons" name="gallons" step="0.001" required 
                   value="<?php echo htmlspecialchars($entry['gallons']); ?>"
                   oninput="calculatePPG()">
        </div>

        <div id="ppgDisplay" class="calculated">
            Price per gallon: $<?php echo number_format($entry['price_per_gallon'], 3); ?>
        </div>

        <input type="submit" value="Update Entry">
    </form>

    <script>
        function calculatePPG() {
            const amount = parseFloat(document.getElementById('amount').value) || 0;
            const gallons = parseFloat(document.getElementById('gallons').value) || 0;
            const ppg = gallons > 0 ? (amount / gallons).toFixed(3) : '0.000';
            document.getElementById('ppgDisplay').textContent = `Price per gallon: $${ppg}`;
        }
    </script>

    <?php footer(); ?>
</body>
</html>
