<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch Image Resizer</title>
</head>
<body>
    <h1>Batch Image Resizer</h1>
    <form action="batch_resize.php" method="post" enctype="multipart/form-data">
        <p>
            <label for="images">Select multiple images:</label><br>
            <input type="file" name="images[]" id="images" accept="image/*,.webp" multiple required>
        </p>
        <p>
            <label for="width">New Width:</label><br>
            <input type="number" name="width" id="width" placeholder="Enter new width" required>
        </p>
        <p>
            <label for="height">New Height:</label><br>
            <input type="number" name="height" id="height" placeholder="Enter new height" required>
        </p>
        <p>
    <label for="output_format">Output Format:</label><br>
    <select name="output_format" id="output_format" required>
        <option value="jpg">JPEG</option>
        <option value="png">PNG</option>
        <option value="gif">GIF</option>
        <option value="webp">WebP</option>
    </select>
</p>
        <input type="submit" value="Resize Images">
    </form>
</body>
</html>