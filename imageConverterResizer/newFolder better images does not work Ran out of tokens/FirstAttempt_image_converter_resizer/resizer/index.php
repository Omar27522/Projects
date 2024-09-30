<?php
list($width, $height, $type, $attr) = getimagesize("flag.jpg");
echo "<img src=\"flag.jpg\" $attr alt=\"getimagesize() example\" />";
?>
<hr>
<img src="flag.jpg" alt="image">


<?php
// Load the image
$source = imagecreatefromjpeg('flag.jpg');
list($width, $height) = getimagesize('flag.jpg');

// Define new dimensions (200x200 pixels)
$newWidth = 100;
$newHeight = 50;

// Create a new image
$thumb = imagecreatetruecolor($newWidth, $newHeight);

// Resize
imagecopyresized($thumb, $source, 0, 0, 0, 0, $newWidth, $newHeight, $width, $height);

// Save the resized image
imagejpeg($thumb, 'resized_image2.jpg', 100);
?>

<!--Thanks to: https://cloudinary.com/guides/bulk-image-resize/resize-image-in-php-a-developers-guide-to-efficient-image-manipulation -->