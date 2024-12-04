<?php
class Database {
    private $articlesFile = 'data/articles.txt';

    public function __construct() {
        // Ensure the data directory exists
        if (!file_exists('data')) {
            mkdir('data', 0777, true);
        }
        
        // Create articles file if it doesn't exist
        if (!file_exists($this->articlesFile)) {
            file_put_contents($this->articlesFile, '');
        }
    }

    public function saveArticle($article) {
        $timestamp = date('Y-m-d h:i:s A T');
        $content = "[{$timestamp}] {$article['title']} by {$article['author']}\n{$article['content']}\n\n";
        return file_put_contents($this->articlesFile, $content, FILE_APPEND);
    }

    public function getArticles() {
        if (!file_exists($this->articlesFile)) {
            return [];
        }
        return array_reverse(file($this->articlesFile));
    }
}
