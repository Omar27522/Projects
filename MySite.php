<!DOCTYPE>
<!--
    You can only interact with this page
    on a php server.###################
    I'm using WAMPSERVER on windows,
    and Pocket PHP on my phone' $$$$
    chage action="MySiteAIO.php" and
    new name button to your file
    -->
<html lang=english>
  <head>
    <title> <?php if (isset($_POST["name"])) {
        $name = $_POST["name"];
        echo $name;
    } else {
        echo "Main Title";
    } ?> </title>
    <meta name="viewport" content="width = device-width
initial-scale=1.0" />
    <style>h1 {color: rgb(14, 66, 14);}
  h2 {color: rgb(66, 66, 198);}
  img {margin: 4px 16px 4px 0;float: right;}
  footer {margin-top: 3%;padding: 20%;position: fixed;bottom: 0;padding-bottom: 0.5rem;}
  body {background-color: #add8e6;margin-right: auto;margin-left: 10%;max-width: 1080px;}
    .sty {background-color: #deeff5;}
    </style>
  </head> <?php $form_field = '
    <form method="post"action="MySiteAIO.php">
        <input type="text" name="name"placeholder="What\'s your name?"/>
        <h2>Pick an Image</h2>
        <label for="fav_img4">
            <img src="https://latinospc.com/images/websites/webcontent/33.jpg"alt="image">
        </label>
            <label for="fav_img3">
                <img src="https://latinospc.com/images/websites/webcontent/44.jpg"alt="image">
            </label>
                <label for="fav_img2">
                    <img src="https://latinospc.com/images/websites/webcontent/1010.jpg"alt="image">
                </label>
                    <label for="fav_img1">
                        <img src="https://latinospc.com/images/websites/webcontent/99.jpg"alt="image">
                    </label>
                        <input type="checkbox" id="fav_img1" name="fav_img1" value="99">
                            <label for="fav_img1">One</label>
                            <br>
                                <input type="checkbox" id="fav_img2" name="fav_img2" value="44">
                                    <label for="fav_img2">Two</label>
                                    <br>
                                        <input type="checkbox" id="fav_img3" name="fav_img3" value="1010">
                                            <label for="fav_img3">Three</label>
                                            <br>
                                                <input type="checkbox" id="fav_img4" name="fav_img4" value="33">
                                                    <label for="fav_img4">Four</label><br />
        <h2 style="text-align:center;"><input type="submit" value="send"/></h2>
    </form>';
$images = array("fav_img1", "fav_img2", "fav_img3", "fav_img4"); ?> <body>
    <header>
      <h1>
        <span class="sty">Welcome!</span>
      </h1> <?php if (isset($_POST["name"])) {
          $name = $_POST["name"];
          if (empty($_POST["name"])) {
              echo "&nbsp;";
          } else {
              echo "Hello, " .
                  $name .
                  '
                <button style="float:right;">
                    <a href="./MySiteAIO.php">New Name?</a>
                </button>
                <hr>';
          }
      } ?>
    </header>
    <main>
      <aside> <?php if (isset($_POST["name"])) {
          echo "";
      } else {
          echo '
                        <span class="sty">' .
              $form_field .
              "</span>";
      } ?> </aside>
      <article>
        <section> <?php if (isset($_POST["name"])) {
            if (empty($_POST["name"])) {
                echo "";
            }
        } ?> </section>
        <section> <?php
        if (isset($_POST["name"])) {
            if (empty($_POST["name"])) {
                echo '
                            <h3>
                                <span class="sty">Do not leave the
                                    <u>name</u> field empty.
                                </span>
                            </h3>
                            <br />' . $form_field;
            }
        }
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            // Check which checkboxes are selected
            $selected_images = [];
            foreach ($images as $image) {
                if (isset($_POST[$image])) {
                    $selected_images[] = $_POST[$image];
                }
            }
            // Display the message if at least one checkbox is selected
            if (!empty($selected_images)) {
                echo '
                            <h2>';
                if (count($selected_images) === 1) {
                    echo "This is the image you picked:";
                } else {
                    echo "These are the images you picked:";
                }
                echo "</h2>";
                foreach ($selected_images as $image_id) {
                    // You can use the $image_id to display the corresponding image or perform other actions
                    // For example:
                    echo '
                            <img src="https://latinospc.com/images/websites/webcontent/' .
                        $image_id .
                        '.jpg" alt="Selected image">';
                }
            } elseif (empty($selected_images)) {
                echo '
                                <h2>You did not select any images</h2>';
                foreach ($selected_images as $image_id) {
                    // You can use the $image_id to display the corresponding image or perform other actions
                    // For example:
                    echo '
                                <img src="https://latinospc.com/images/websites/webcontent/' .
                        $image_id .
                        '.jpg" alt="Selected image">';
                }
            }
        }
        ?> </section>
      </article>
    </main>
    <footer>
      <span style="background-color:#ADD8E6;">By LAtinosPC.com 2024</span>
    </footer>
  </body>
</html>