CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE IF NOT EXISTS app.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar VARCHAR(500),
    bio TEXT,
    gender SMALLINT DEFAULT 0,
    birthday DATE,
    location VARCHAR(255),
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app.posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    images TEXT[],
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    topic VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app.messages (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER REFERENCES app.users(id) ON DELETE CASCADE,
    to_user_id INTEGER REFERENCES app.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app.refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON app.users(username);
CREATE INDEX idx_users_email ON app.users(email);
CREATE INDEX idx_posts_user_id ON app.posts(user_id);
CREATE INDEX idx_posts_created_at ON app.posts(created_at DESC);
CREATE INDEX idx_messages_from_user ON app.messages(from_user_id);
CREATE INDEX idx_messages_to_user ON app.messages(to_user_id);
CREATE INDEX idx_refresh_tokens_user ON app.refresh_tokens(user_id);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON app.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON app.posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
