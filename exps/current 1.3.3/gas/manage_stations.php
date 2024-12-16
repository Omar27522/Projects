<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once '../db_connect.php';
$db = new Database();

header('Content-Type: application/json');
$response = ['success' => false, 'message' => '', 'stations' => [], 'debug' => []];

try {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $response['debug']['post_data'] = $_POST;
        
        if (isset($_POST['action'])) {
            if ($_POST['action'] === 'add' && isset($_POST['station_name'])) {
                $newStation = trim($_POST['station_name']);
                $response['debug']['new_station'] = $newStation;
                
                if (!empty($newStation)) {
                    if ($db->addStation($newStation)) {
                        $response['success'] = true;
                        $response['message'] = 'Station added successfully';
                    } else {
                        $response['message'] = 'Failed to add station. It might already exist.';
                    }
                } else {
                    $response['message'] = 'Station name cannot be empty';
                }
            } elseif ($_POST['action'] === 'delete' && isset($_POST['station_name'])) {
                if ($db->deleteStation($_POST['station_name'])) {
                    $response['success'] = true;
                    $response['message'] = 'Station deleted successfully';
                } else {
                    $response['message'] = 'Failed to delete station';
                }
            }
        } else {
            $response['message'] = 'No action specified';
        }
    } else {
        $response['message'] = 'Invalid request method';
    }

    // Always return the updated list of stations
    $response['stations'] = $db->getAllStations();
    $response['debug']['all_stations'] = $response['stations'];

} catch (Exception $e) {
    $response['success'] = false;
    $response['message'] = 'Server error: ' . $e->getMessage();
    error_log('Station management error: ' . $e->getMessage());
}

echo json_encode($response);
