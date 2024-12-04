<?php
require_once 'models/Article.php';

// Initialize objects
$article = new Article();
$oldFile = 'data/articles.txt';

// Read old file
if (!file_exists($oldFile)) {
    die("Old articles file not found!\n");
}

$lines = file($oldFile);
$currentArticle = '';
$articles = [];

// Process each line
foreach ($lines as $line) {
    if (preg_match('/^\[/', $line)) {
        // If we have a previous article, process it
        if (!empty($currentArticle)) {
            $converted = $article->convertFromText($currentArticle);
            if ($converted) {
                $articles[] = $converted;
            }
        }
        $currentArticle = $line;
    } else {
        $currentArticle .= $line;
    }
}

// Process the last article
if (!empty($currentArticle)) {
    $converted = $article->convertFromText($currentArticle);
    if ($converted) {
        $articles[] = $converted;
    }
}

// Create backup of old file
copy($oldFile, $oldFile . '.backup');

// Save all articles using new JSON format
foreach ($articles as $articleData) {
    $article->create($articleData['title'], $articleData['content'], $articleData['author']);
}

echo "Migration completed successfully!\n";
echo "Total articles migrated: " . count($articles) . "\n";
echo "A backup of your old articles has been created at: {$oldFile}.backup\n";
