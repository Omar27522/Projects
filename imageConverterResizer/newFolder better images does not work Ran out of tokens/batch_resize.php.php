<?php
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
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $new_width = intval($_POST['width']);
    $new_height = intval($_POST['height']);
    $output_format = $_POST['output_format'];
    
    $upload_dir = 'resized_images/';
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir, 0755, true);
    }
    
    $success_count = 0;
    $error_count = 0;
    
    foreach ($_FILES['images']['tmp_name'] as $key => $tmp_name) {
        if ($_FILES['images']['error'][$key] === UPLOAD_ERR_OK) {
            $original_filename = $_FILES['images']['name'][$key];
            $file_info = pathinfo($original_filename);
            //$new_filename = 'resized_' . $original_filename;
            $new_filename = 'resized_' . $file_info['filename'] . '.' . $output_format;
            $destination_path = $upload_dir . $new_filename;
            
            if (resizeImage($tmp_name, $destination_path, $new_width, $new_height)) {
                $success_count++;
            } else {
                $error_count++;
            }
        } else {
            $error_count++;
        }
    }
    
    echo "<h2>Batch Resize Results</h2>";
    echo "<p>Successfully resized images: $success_count</p>";
    echo "<p>Failed to resize images: $error_count</p>";
    
    // Display resized images
    echo "<h3>Resized Images:</h3>";
    $resized_images = glob($upload_dir . "resized_*");
    foreach ($resized_images as $image) {
        echo "<img src='$image' alt='Resized Image' style='max-width: 200px; margin: 10px;'>";
    }
} else {
    echo "<p>No images were uploaded. Please use the form to upload images.</p>";
}
?>