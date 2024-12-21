<?php
require_once '../db_connect.php';

if (isset($_GET['id'])) {
    $db = new Database();
    if ($db->deleteGasEntry($_GET['id'])) {
        header('Location: index.php?message=Entry deleted successfully&type=success');
    } else {
        header('Location: index.php?message=Error deleting entry&type=error');
    }
} else {
    header('Location: index.php?message=Invalid request&type=error');
}
exit();
?>
