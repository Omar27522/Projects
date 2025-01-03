<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Document</title>
</head>
<body>
    <header>
        <nav>
            <?php include 'code.php';
                breadCrumbs();
            ?>
        </nav>
        <h1>New Expense</h1>
    </header>

    <h6>
    The idea for this app is to Make a simple app that will connect to a database.
        The app has to be robust enough to require minimum maintenance.
        And it must follow Agile Principles.
    </h6>
    <footer>
        <?php
            breadCrumbs();
        ?>
    </footer>
</body>
</html>