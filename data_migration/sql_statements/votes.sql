CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,
    post_id INT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    result SMALLINT NOT NULL,
    CONSTRAINT result_value_check CHECK(
        (result = 1) OR (result = -1)
    ),
    UNIQUE(post_id, user_id)
);