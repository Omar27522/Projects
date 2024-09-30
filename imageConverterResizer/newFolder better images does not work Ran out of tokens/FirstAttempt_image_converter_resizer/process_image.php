<!DOCTYPE html>
<html>
<head>
    <!-- /*
    I have this code:
    <form action="process_image.php" method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*">
        <input type="submit" value="Submit">
    </form>
    I would like to show what the file that was uploaded was, when I navigate to process_image.php
    -->

    <h1>Gemini release 2024.09.04</h1>

<!-- This code does the following:

    Checks for an uploaded image:
        It verifies if an image was submitted through the form by checking if the
            $_FILES['image'] array is set and if there's no upload error.

    Gets file information:
        If an image was uploaded, it retrieves the temporary file path and the original filename.

    Sets the destination path:
        It specifies the desired destination path for the uploaded image, which is uploads/ followed by the original filename.

    Moves the uploaded file:
        It moves the uploaded file from its temporary location to the specified destination path using move_uploaded_file().

    Displays the image:
        If the file was moved successfully, it displays the uploaded image using an
            <img> tag with the destination path as the source. If there was an error, it displays an error message.

    Handles no upload:
        If no image was uploaded, it displays a message indicating that.

        **Make sure to create the uploads directory in your project's root directory to store the uploaded images.**
-->
    <title>Uploaded Image</title>
</head>
<body>
    <?php
    // Check if an image was uploaded
    if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
        // Get temporary file path and original filename
        $tmp_name = $_FILES['image']['tmp_name'];
        $original_filename = $_FILES['image']['name'];

        // Set the desired destination path for the uploaded image
        $destination_path = 'uploads/' . $original_filename;

        // Move the uploaded file to its final destination
        if (move_uploaded_file($tmp_name, $destination_path)) {
            // Display the uploaded image
            echo $original_filename.'<br/>';
            echo '<img src="' . $destination_path . '" alt="Uploaded Image">';
        } else {
            echo 'Error uploading the image.';
        }
    } else {
        echo 'No image was uploaded.';
    }

    // The image gets displayed, maybe the index can be modified so that it adjusts to the user's requirements we can adjust the values directly on the form, just like the example above.
    /*
                <form action="process_image.php" method="post" enctype="multipart/form-data">
                    <input type="file" name="image" accept="image/*">
                    <input type="submit" value="Submit">
                </form>
    */
    // There is some design involved, which will bring the project together nicely.
    ?>
</body>
</html>