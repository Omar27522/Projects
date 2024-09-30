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
        case IMAGETYPE_WEBP:
            $source = imagecreatefromwebp($source_path);
            break;
        default:
            return false;
    }
    
    $thumb = imagecreatetruecolor($new_width, $new_height);
    
    // Preserve transparency for PNG and WebP
    if ($type == IMAGETYPE_PNG || $type == IMAGETYPE_WEBP) {
        imagealphablending($thumb, false);
        imagesavealpha($thumb, true);
        $transparent = imagecolorallocatealpha($thumb, 255, 255, 255, 127);
        imagefilledrectangle($thumb, 0, 0, $new_width, $new_height, $transparent);
    }
    
    imagecopyresampled($thumb, $source, 0, 0, 0, 0, $new_width, $new_height, $width, $height);
    
    $output_type = pathinfo($dest_path, PATHINFO_EXTENSION);
    
    switch (strtolower($output_type)) {
        case 'jpg':
        case 'jpeg':
            imagejpeg($thumb, $dest_path, 90);
            break;
        case 'png':
            imagepng($thumb, $dest_path, 9);
            break;
        case 'gif':
            imagegif($thumb, $dest_path);
            break;
        case 'webp':
            imagewebp($thumb, $dest_path, 80);
            break;
        default:
            return false;
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
        echo '<h2>Image Processed Successfully</h2>';
        echo '<p>New filename: ' . htmlspecialchars($new_filename) . '</p>';
        echo '<p>Dimensions: ' . $new_width . 'x' . $new_height . '</p>';
        echo '<p><a href="./"><button>Upload Another?</button></a></p>';
        echo '<img src="' . htmlspecialchars($destination_path) . '" alt="Resized Image">';
    } else {
        echo '<p>Error processing the image.</p>';
        echo '<p><a href="./"><button>Go Back</button></a></p>';
    }
} else {
    echo '<p>No image was uploaded or an error occurred.</p>';
    echo '<p><a href="./"><button>Go Back</button></a></p>';
}
?>