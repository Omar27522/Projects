<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Read the existing JSON files
    $expensesFile = 'expenses.json';
    $configFile = 'config.json';
    
    $jsonData = file_get_contents($expensesFile);
    $configData = file_get_contents($configFile);
    
    $data = json_decode($jsonData, true);
    $config = json_decode($configData, true);

    // Get the form data
    $newExpense = [
        'date' => $_POST['date'],
        'item' => $_POST['item'],
        'place' => $_POST['place'],
        'amount' => '$' . $_POST['amount'],
        'type' => $_POST['type']
    ];

    // Check if item exists in config, if not add it
    $itemExists = false;
    foreach ($config['items'] as $item) {
        if ($item['name'] === $_POST['item']) {
            $itemExists = true;
            break;
        }
    }

    if (!$itemExists) {
        // Add new item to config
        $config['items'][] = [
            'name' => $_POST['item'],
            'category' => $_POST['type']
        ];

        // Sort items alphabetically
        usort($config['items'], function($a, $b) {
            return strcasecmp($a['name'], $b['name']);
        });

        // Save updated config
        file_put_contents($configFile, json_encode($config, JSON_PRETTY_PRINT));
    }

    // Add the new expense
    $data['expenses'][] = $newExpense;

    // Save the updated expenses
    if (file_put_contents($expensesFile, json_encode($data, JSON_PRETTY_PRINT))) {
        echo json_encode(['success' => true]);
    } else {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to save data']);
    }
} else {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
}
?>
