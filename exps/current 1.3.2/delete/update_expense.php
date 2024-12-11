<?php
require_once 'db_connect.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $db = new Database();
    $id = $_POST['id'] ?? null;
    $date = $_POST['date'] ?? null;
    $item = $_POST['item'] ?? null;
    $place = $_POST['place'] ?? null;
    $amount = $_POST['amount'] ?? null;
    $type = $_POST['type'] ?? null;

    if ($id && $date && $item && $place && $amount && $type) {
        try {
            $result = $db->updateExpense($id, $date, $item, $place, floatval($amount), $type);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Expense updated successfully']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to update expense']);
            }
        } catch (Exception $e) {
            echo json_encode(['success' => false, 'message' => $e->getMessage()]);
        }
    } else {
        echo json_encode(['success' => false, 'message' => 'Missing required fields']);
    }
} else {
    echo json_encode(['success' => false, 'message' => 'Invalid request method']);
}
