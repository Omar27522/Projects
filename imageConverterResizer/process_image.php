<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Document</title>
</head>
<body>
<?php
// Function to generate a unique filename
function generateUniqueFilename($original_filename) {
    $extension = pathinfo($original_filename, PATHINFO_EXTENSION);
    return uniqid() . '.' . $extension;
}

// Function to resize image
function resizeImage($source_path, $dest_path, $new_width, $new_height) {
    list($width, $height, $type) = getimagesize($source_path);

    switch ($type) {
        case IMAGETYPE_JPEG:
            $source = imagecreatefromjpeg($source_path);
            break;
        case IMAGETYPE_PNG:
            $source = imagecreatefrompng($source_path);
            break;
        case IMAGETYPE_GIF:
            $source = imagecreatefromgif($source_path);
            break;
        default:
            return false;
    }

    $thumb = imagecreatetruecolor($new_width, $new_height);
    imagecopyresampled($thumb, $source, 0, 0, 0, 0, $new_width, $new_height, $width, $height);

    switch ($type) {
        case IMAGETYPE_JPEG:
            imagejpeg($thumb, $dest_path, 90);
            break;
        case IMAGETYPE_PNG:
            imagepng($thumb, $dest_path, 9);
            break;
        case IMAGETYPE_GIF:
            imagegif($thumb, $dest_path);
            break;
    }

    imagedestroy($source);
    imagedestroy($thumb);
    return true;
}

// Main processing logic
if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
    $tmp_name = $_FILES['image']['tmp_name'];
    $original_filename = $_FILES['image']['name'];
    $new_filename = !empty($_POST['name']) ? $_POST['name'] : generateUniqueFilename($original_filename);

    $upload_dir = 'uploads/';
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir, 0755, true);
    }

    $destination_path = $upload_dir . $new_filename;

    $new_width = !empty($_POST['width']) ? intval($_POST['width']) : 100;
    $new_height = !empty($_POST['height']) ? intval($_POST['height']) : 100;

    if (resizeImage($tmp_name, $destination_path, $new_width, $new_height)) {
        echo '<h2 class="file">Image Processed Successfully</h2>';
        echo '<p class="file">New filename: ' . htmlspecialchars($new_filename) . '</p>';
        echo '<p class="file">Dimensions: ' . $new_width . 'x' . $new_height . '</p>';
        echo '<p class="file"><a href="./"><button>Upload Another?</button></a></p>';
        echo '<img src="' . htmlspecialchars($destination_path) . '" alt="Resized Image">';
    } else {
        echo '<p class="file">Error processing the image.</p>';
        echo '<p class="file"><a href="./"><button>Go Back</button></a></p>';
    }
} else {
    echo '<p class="file">No image was uploaded or an error occurred.</p>';
    echo '<p class="file"><a href="./"><button>Go Back</button></a></p>';
}
?>
</body>
</html>
