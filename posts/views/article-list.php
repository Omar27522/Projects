<div class="container">
    <h3>Browse Articles</h3>
    <?php
    if (empty($articles)) {
        echo '<p>No articles available yet.</p>';
    } else {
        foreach ($articles as $line) {
            $article = $controller->parseArticle($line);
            if ($article) {
                echo '<div class="article-item">';
                echo '<div class="article-timestamp">' . htmlspecialchars($article['timestamp']) . '</div>';
                echo '<div class="article-title">' . htmlspecialchars($article['title']) . '</div>';
                echo '<div class="article-author">By ' . htmlspecialchars($article['author']) . '</div>';
                echo '<div class="article-content">' . htmlspecialchars($article['content']) . '</div>';
                echo '</div>';
            }
        }
    }
    ?>
