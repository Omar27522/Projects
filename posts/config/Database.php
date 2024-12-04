<?php
class Database {
    private $dataDir = 'data';
    private $currentFile;

    public function __construct() {
        // Ensure the data directory exists
        if (!file_exists($this->dataDir)) {
            mkdir($this->dataDir, 0777, true);
        }
        
        // Set current file based on current month
        $this->currentFile = $this->getMonthlyFilePath();
        
        // Create current month's file if it doesn't exist
        if (!file_exists($this->currentFile)) {
            $this->initializeJsonFile($this->currentFile);
        }
    }

    private function getMonthlyFilePath() {
        $year = date('Y');
        $month = date('m');
        $dir = "{$this->dataDir}/{$year}";
        
        if (!file_exists($dir)) {
            mkdir($dir, 0777, true);
        }
        
        return "{$dir}/{$month}.json";
    }

    private function initializeJsonFile($file) {
        file_put_contents($file, json_encode(['articles' => []], JSON_PRETTY_PRINT));
    }

    public function saveArticle($article) {
        // Check if we need to create a new month's file
        $currentFile = $this->getMonthlyFilePath();
        if ($currentFile !== $this->currentFile) {
            $this->currentFile = $currentFile;
            if (!file_exists($this->currentFile)) {
                $this->initializeJsonFile($this->currentFile);
            }
        }

        // Read existing content
        $content = json_decode(file_get_contents($this->currentFile), true);
        
        // Add new article with timestamp
        $article['id'] = uniqid();
        $article['timestamp'] = date('Y-m-d h:i:s A T');
        $content['articles'][] = $article;

        // Save back to file
        return file_put_contents($this->currentFile, json_encode($content, JSON_PRETTY_PRINT));
    }

    public function getArticles() {
        $articles = [];
        
        // Get all year directories
        $yearDirs = glob($this->dataDir . '/*', GLOB_ONLYDIR);
        
        foreach ($yearDirs as $yearDir) {
            // Get all month files
            $monthFiles = glob($yearDir . '/*.json');
            
            foreach ($monthFiles as $file) {
                if (file_exists($file)) {
                    $content = json_decode(file_get_contents($file), true);
                    if (isset($content['articles'])) {
                        $articles = array_merge($articles, $content['articles']);
                    }
                }
            }
        }
        
        // Sort by timestamp in descending order
        usort($articles, function($a, $b) {
            return strtotime($b['timestamp']) - strtotime($a['timestamp']);
        });
        
        return $articles;
    }
}
