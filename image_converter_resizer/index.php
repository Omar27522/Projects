<p>Claude AI's Take on Image Converter and Resizer. <a href="claude.php">Link</a></p>

<?php
$br='<br />';
$v = "I would love to edit an image.$br $br
From a list of formats the script automatically modifies the image to the desired size, type, and quality.$br $br
Basically I want the script to choose the best image quality while maintaining a small size, at the desired resolution.";
?>


<input type="file" name="image" accept="image/*">
<br /><hr><br />
Name:<br /><input type="text" value="" >
<br />
Size: <br />
<input type="text" value="Height">
<input type="text" value="Width">
<br /><br />
JPG:<input type="radio" value="Desired Type" >
Webp:<input type="radio" value="Desired Type" >
PNG:<input type="radio" value="Desired Type" >
<br />
Quality: <input type="range" value="Desired Quality" >
<br />
<input type="button" onclick="alert('PICK THE LOCATION OF THE NEW IMAGE')" value="Location">
<br /><br />
<input type="submit" value="Submit">
<H1><?=$v?></H1>


<!-- Here are teh image functions I will need
    https://www.php.net/manual/en/ref.image.php

    https://www.php.net/manual/en/refs.utilspec.image.php
-->