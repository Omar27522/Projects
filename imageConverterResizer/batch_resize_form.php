<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Batch Image Resizer</title>
</head>
<body>
    <h1>Batch Image Resizer</h1>
    <a href="./" class="wright"><h3>Choose Single File</h3></a><br/>
    <form action="batch_resize.php" method="post" enctype="multipart/form-data">
        <p>
            <input class="file" type="file" name="images[]" id="images" accept="image/*" multiple required>
        </p>
        <p>
            <label for="width">New Width:</label><br>
            <input type="number" name="width" id="width" placeholder="Enter new width" required>
        </p>
        <p>
            <label for="height">New Height:</label><br>
            <input type="number" name="height" id="height" placeholder="Enter new height" required>
        </p>
        <input type="submit" value="Submit">
    </form>
</body>
</html>