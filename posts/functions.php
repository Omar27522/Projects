<?php

/**
 * Article Management Functions
 */

function saveArticle($title, $content, $author) {
    $timestamp = date('Y-m-d h:i:s A T');
    $content = "[{$timestamp}] {$title} by {$author}\n{$content}\n\n";
    return file_put_contents('articles.txt', $content, FILE_APPEND);
}

function getArticles() {
    if (!file_exists('articles.txt')) {
        return [];
    }
    return array_reverse(file('articles.txt'));
}

function parseArticle($line) {
    if (preg_match('/\[(.*?)\] (.*) by (.*)/', $line, $matches)) {
        return [
            'timestamp' => $matches[1],
            'title' => $matches[2],
            'author' => $matches[3],
            'content' => substr($line, strpos($line, "\n") + 1)
        ];
    }
    return null;
}

/**
 * Display Functions
 */

function displayArticle($article) {
    if (!$article) return;
    
    echo '<div class="article-item">';
    echo '<div class="article-timestamp">' . htmlspecialchars($article['timestamp']) . '</div>';
    echo '<div class="article-title">' . htmlspecialchars($article['title']) . '</div>';
    echo '<div class="article-author">By ' . htmlspecialchars($article['author']) . '</div>';
    echo '<div class="article-content">' . htmlspecialchars($article['content']) . '</div>';
    echo '</div>';
}

function displayArticles() {
    $articles = getArticles();
    
    if (empty($articles)) {
        echo '<p>No articles available yet.</p>';
        return;
    }

    foreach ($articles as $line) {
        $article = parseArticle($line);
        displayArticle($article);
    }
}

function displaySuccessMessage($message) {
    echo '<div class="post-success">' . htmlspecialchars($message) . '</div>';
}

/**
 * Form Processing Functions
 */

function processArticleSubmission() {
    if (!isset($_POST['articleTitle'], $_POST['articleContent'], $_POST['authorName'])) {
        return false;
    }

    $title = trim($_POST['articleTitle']);
    $content = trim($_POST['articleContent']);
    $author = trim($_POST['authorName']);

    // Basic validation
    if (empty($title) || empty($content) || empty($author)) {
        return false;
    }

    return saveArticle($title, $content, $author);
}

/**
 * Navigation Functions
 */

function isActiveTab($tabName) {
    return (!isset($_GET['tab']) && $tabName === 'input') || 
           (isset($_GET['tab']) && $_GET['tab'] === $tabName);
}

function getTabClass($tabName) {
    return 'tab' . (isActiveTab($tabName) ? ' active' : '');
}
