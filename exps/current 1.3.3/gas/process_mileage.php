<?php
require_once '../db_connect.php';

function saveMileageData($first_miles, $last_miles, $prev_total) {
    try {
        $db = new Database();
        
        // If only first miles provided, just save it and return
        if (empty($last_miles)) {
            return [
                'success' => true,
                'message' => 'First miles reading saved',
                'first_miles' => $first_miles
            ];
        }
        
        // Calculate monthly total
        $monthly_total = $last_miles - $first_miles;
        
        // Calculate new cumulative total
        $new_total = $prev_total + $monthly_total;
        
        // Get current month and year
        $month = date('Y-m');
        
        $sql = "INSERT INTO mileage_tracking (month, first_miles, last_miles, monthly_total, cumulative_total) 
                VALUES (:month, :first_miles, :last_miles, :monthly_total, :cumulative_total)";
        
        $db->query($sql, [
            ':month' => $month,
            ':first_miles' => $first_miles,
            ':last_miles' => $last_miles,
            ':monthly_total' => $monthly_total,
            ':cumulative_total' => $new_total
        ]);

        return [
            'success' => true,
            'monthly_total' => $monthly_total,
            'new_total' => $new_total,
            'message' => 'Mileage data saved successfully'
        ];
    } catch(PDOException $e) {
        return [
            'success' => false,
            'message' => 'Error saving mileage data: ' . $e->getMessage()
        ];
    }
}

function getLatestMileageData() {
    try {
        $db = new Database();
        $sql = "SELECT * FROM mileage_tracking ORDER BY created_at DESC LIMIT 1";
        $stmt = $db->query($sql);
        return $stmt->fetch(PDO::FETCH_ASSOC);
    } catch(PDOException $e) {
        return null;
    }
}

// Handle POST request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $first_miles = floatval($_POST['first_miles'] ?? 0);
    $last_miles = !empty($_POST['last_miles']) ? floatval($_POST['last_miles']) : null;
    $first_total = floatval($_POST['first_total'] ?? 0);

    if ($last_miles && $last_miles < $first_miles) {
        echo json_encode([
            'success' => false,
            'message' => 'Last miles cannot be less than first miles'
        ]);
        exit;
    }

    $result = saveMileageData($first_miles, $last_miles, $first_total);
    echo json_encode($result);
    exit;
}
?>
