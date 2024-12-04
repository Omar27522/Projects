<?php
require_once 'config/Database.php';

class Article {
    private $db;

    public function __construct() {
        $this->db = new Database();
    }

    public function create($title, $content, $author) {
        // Validate input
        if (empty($title) || empty($content) || empty($author)) {
            return false;
        }

        $article = [
            'title' => $title,
            'content' => $content,
            'author' => $author
        ];

        return $this->db->saveArticle($article);
    }

    public function getAll() {
        return $this->db->getArticles();
    }
}
