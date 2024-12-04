<?php
session_start();
date_default_timezone_set('America/Los_Angeles');

require_once 'controllers/ArticleController.php';
require_once 'helpers/functions.php';

// Initialize controller
$controller = new ArticleController();

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if ($controller->create($_POST)) {
        $_SESSION['post_success'] = true;
    }
}

// Get all articles for display
$articles = $controller->index();

// Include view files
require_once 'views/header.php';

if (isActiveTab('input')) {
    require_once 'views/article-form.php';
} else {
    require_once 'views/article-list.php';
}

require_once 'views/footer.php';