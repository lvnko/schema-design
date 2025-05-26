CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    url VARCHAR(400),
    content TEXT,
    topic_id INT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    CONSTRAINT url_content_not_both_null CHECK(
        (url IS NOT NULL) OR (content IS NOT NULL)
    )
);