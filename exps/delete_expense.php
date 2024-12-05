<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $expensesFile = 'expenses.json';
    
    // Read the existing expenses
    $jsonData = file_get_contents($expensesFile);
    $data = json_decode($jsonData, true);
    
    // Get the index to delete
    $index = isset($_POST['index']) ? intval($_POST['index']) : -1;
    
    if ($index >= 0 && $index < count($data['expenses'])) {
        // Remove the expense at the specified index
        array_splice($data['expenses'], $index, 1);
        
        // Save the updated expenses
        if (file_put_contents($expensesFile, json_encode($data, JSON_PRETTY_PRINT))) {
            echo json_encode(['success' => true]);
        } else {
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => 'Failed to save data']);
        }
    } else {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid index']);
    }
} else {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
}
?>
