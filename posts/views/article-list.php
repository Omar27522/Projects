<div class="container">
    <h3>Browse Articles</h3>
    <?php
    if (empty($articles)) {
        echo '<p>No articles available yet.</p>';
    } else {
        foreach ($articles as $article) {
            echo '<details class="article-item">';
            echo '<summary class="article-header">';
            echo '<div class="article-meta">';
            echo '<div class="article-title">' . htmlspecialchars($article['title']) . '</div>';
            echo '<div class="article-info">';
            echo '<span class="article-timestamp">' . htmlspecialchars($article['timestamp']) . '</span>';
            echo '<span class="article-author">By ' . htmlspecialchars($article['author']) . '</span>';
            echo '</div>';
            echo '</div>';
            echo '<div class="expand-icon">▼</div>';
            echo '</summary>';
            echo '<div class="article-content">' . nl2br(htmlspecialchars($article['content'])) . '</div>';
            echo '</details>';
        }
    }
    ?>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const details = document.querySelectorAll('details');
    
    details.forEach(detail => {
        detail.addEventListener('toggle', function() {
            if (this.open) {
                // Close other details when one is opened
                details.forEach(d => {
                    if (d !== this && d.open) d.open = false;
                });
                
                // Scroll the opened details into view if needed
                const rect = this.getBoundingClientRect();
                const isInViewport = rect.top >= 0 && rect.bottom <= window.innerHeight;
                
                if (!isInViewport) {
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    });
});
</script>
