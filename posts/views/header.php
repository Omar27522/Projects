<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Community Articles Hub</title>
    <link rel="stylesheet" href="./assets/css/consolidated-styles.css">
</head>
<body>
    <header class="site-header">
        <h1>Welcome to Our Community Hub</h1>
        <p>Share and discover interesting articles with the community</p>
    </header>

    <div class="tabs">
        <button class="<?php echo getTabClass('input'); ?>"
            onclick="window.location.href='?tab=input'">Post Article</button>
        <button class="<?php echo getTabClass('history'); ?>"
            onclick="window.location.href='?tab=history'">Browse Articles</button>
    </div>
