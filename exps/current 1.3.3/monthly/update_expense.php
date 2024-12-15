<?php
require_once '../db_connect.php';

header('Content-Type: application/json');

try {
    if (!isset($_POST['id'])) {
        throw new Exception('ID is required');
    }

    $db = new Database();
    $id = $_POST['id'];
    $submittedDate = $_POST['date'];
    $item = $_POST['item'];
    $place = $_POST['place'];
    $amount = $_POST['amount'];
    $type = $_POST['type'];

    // Set timezone to Los Angeles
    date_default_timezone_set('America/Los_Angeles');
    
    // Get current time
    $currentTime = date("g:i A");
    
    // Remove any existing time from the submitted date
    $submittedDate = preg_replace('/\d+:\d+\s*[AaPp][Mm]/', '', $submittedDate);
    $submittedDate = trim($submittedDate);
    
    // Format the date to match our database format
    $dateObj = DateTime::createFromFormat('M j', $submittedDate, new DateTimeZone('America/Los_Angeles'));
    
    if ($dateObj === false) {
        throw new Exception('Invalid date format: ' . $submittedDate . ' (Expected format: M j)');
    }
    
    $formattedDate = $dateObj->format('M j') . ' ' . $currentTime;

    $result = $db->updateExpense($id, $formattedDate, $item, $place, $amount, $type);

    if ($result) {
        echo json_encode(['success' => true, 'message' => 'Expense updated successfully']);
    } else {
        echo json_encode(['success' => false, 'message' => 'Failed to update expense']);
    }
} catch (Exception $e) {
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
