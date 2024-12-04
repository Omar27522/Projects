<?php
require_once 'models/Article.php';

class ArticleController {
    private $model;

    public function __construct() {
        $this->model = new Article();
    }

    public function index() {
        return $this->model->getAll();
    }

    public function create($data) {
        if (!isset($data['articleTitle'], $data['articleContent'], $data['authorName'])) {
            return false;
        }

        return $this->model->create(
            trim($data['articleTitle']),
            trim($data['articleContent']),
            trim($data['authorName'])
        );
    }

    public function parseArticle($line) {
        return $this->model->parse($line);
    }
}
