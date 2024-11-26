<?php
// I need to search for file names keywords, and show only the ones I have searched for.
$folderPath = './'; // Update with your folder path
$searchKeyword = isset($_GET['search']) ? $_GET['search'] : '';

// Array to store image paths
$imagePaths = array();

// Open the directory
if ($handle = opendir($folderPath)) {
    // Loop through the directory contents
    while (false !== ($entry = readdir($handle))) {
        // Skip the current and parent directory entries
        if ($entry != "." && $entry != "..") {
            // Check if the entry is a file and has a valid image extension
            $fileExtension = pathinfo($entry, PATHINFO_EXTENSION);
            $validExtensions = ['jpg', 'jpeg', 'png', 'gif'];

            if (in_array(strtolower($fileExtension), $validExtensions)) {
                // Check if the entry matches the search keyword
                if ($searchKeyword === '' || stripos($entry, $searchKeyword) !== false) {
                    $imagePaths[] = $folderPath . '/' . $entry;
                }
            }
        }
    }
    // Close the directory
    closedir($handle);
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Viewer</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: left;
        }
        #image-container img {
            width: 100%;
            position: absolute;
        }
        #image-container a {
            position: absolute;
            width: 100%;
        }
    </style>
</head>

<body>
    <form method="GET" style="margin-bottom: 20px;">
        <input type="text" name="search" value="<?php echo htmlspecialchars($searchKeyword); ?>" placeholder="Search for images...">
        <button type="submit">Search</button>
    </form>

    <div id="image-container"></div>

    <script>
    var images = <?php echo json_encode($imagePaths); ?>;
    var preloadedImages = [];
    var currentIndex = 0;

    // Preload images
    for (var i = 0; i < images.length; i++) {
        var img = new Image();
        img.src = images[i];
        preloadedImages.push(img);
    }

    function showImage(index) {
        var img = preloadedImages[index];
        img.style.width = "400px";
        img.style.position = "absolute";
        var container = document.getElementById('image-container');
        container.innerHTML = "";
        var link = document.createElement('a');
        link.href = images[index];
        link.target = "_blank";
        link.appendChild(img);
        container.appendChild(link);
    }

    document.addEventListener("keydown", function(event) {
        if (event.key === "ArrowRight") {
            currentIndex++;
            if (currentIndex >= preloadedImages.length) {
                currentIndex = 0; // Loop back to the first image
            }
            showImage(currentIndex);
        } else if (event.key === "ArrowLeft") {
            currentIndex--;
            if (currentIndex < 0) {
                currentIndex = preloadedImages.length - 1; // Loop back to the last image
            }
            showImage(currentIndex);
        }
    });

    // Show the first image initially
    if (preloadedImages.length > 0) {
        showImage(currentIndex);
    }
    </script>
</body>

</html>
