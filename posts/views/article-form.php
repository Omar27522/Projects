<div class="container">
    <?php if (isset($_SESSION['post_success'])): ?>
        <div class="post-success">Your article has been successfully posted!</div>
        <?php unset($_SESSION['post_success']); ?>
    <?php endif; ?>

    <form method="POST">
        <div class="form-group">
            <label for="articleTitle">Article Title:</label>
            <input type="text" id="articleTitle" name="articleTitle" required>
        </div>
        <div class="form-group">
            <label for="articleContent">Article Content:</label><br />
            <textarea id="articleContent" name="articleContent" rows="10" required></textarea>
        </div>
        <div class="form-group">
            <label for="authorName">Your Name:</label>
            <input type="text" id="authorName" name="authorName" required>
        </div>
        <button type="submit" class="submit-btn">Post Article</button>
    </form>
</div>
