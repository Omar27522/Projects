<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <script src="table_sort.js" defer></script>
    <title>Expenses</title>
</head>

<body>
    <h1>New Expense</h1>
    <form method="POST" action="">
        <section>
            <input type="text" name="date" placeholder="Date"
                value="<?php date_default_timezone_set("America/Los_Angeles"); echo date("M-j"); ?>" required>
            <hr><input type="text" name="item" placeholder="Item" required id="item">
            <hr><input type="text" name="place" placeholder="Place" required>
            <hr><input type="number" step="1" name="amount" placeholder="Amount" min="0" required>
            <hr><select name="type" required>
                <option value="">Type</option>
                <option value="misc">Misc</option>
                <option value="food">Food</option>
                <option value="entertainment">Entertainment</option>
                <option value="tithe">Tithe</option>
                <option value="repairs">Repairs</option>
                <option value="maintenance">Maintenance</option>
                <option value="clothing">Clothing</option>
                <option value="gifts">Gifts</option>
                <option value="personal">Personal</option>
                <option value="tax">Tax</option>
            </select>
        </section>
        <input type="submit" value="Add Expense">
    </form>
    <?php
    require_once 'db_connect.php';
    $db = new Database();
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Format the date properly
        $submittedDate = $_POST['date'];
        $currentTime = date("g:i A");
        // Convert to proper ISO format
        $dateObj = DateTime::createFromFormat('M-j g:i A', $submittedDate . ' ' . $currentTime, new DateTimeZone('America/Los_Angeles'));
        if ($dateObj === false) {
            $error = "Error: Invalid date format";
        } else {
            $dateWithTime = $dateObj->format('Y-m-d H:i:s');
            $result = $db->addExpense(
                $dateWithTime,
                $_POST['item'],
                $_POST['place'],
                $_POST['amount'],
                $_POST['type']
            );
            if ($result) {
                // Redirect to prevent form resubmission
                echo "<a style=\"display:inline-block;border:none;\" href='index.php#item'><p style='color: green;'>Expenses will be added successfully!</p></a>";
                //header('Location: ' . $_SERVER['PHP_SELF'] . '?success=1');
            } else {
                $error = "Error adding expense.";
            }
        }
    }
    require_once 'db_connect.php';
     footer();
    ?>

</body>

</html>