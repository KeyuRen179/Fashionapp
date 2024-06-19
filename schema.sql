-- schema.sql

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS user_searches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    search_query TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    user_searches_id INTEGER NOT NULL,
    image_name VARCHAR(1000) NOT NULL,
    FOREIGN KEY (user_searches_id) REFERENCES user_searches(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS weblinks (
    id SERIAL PRIMARY KEY,
    user_searches_id INTEGER NOT NULL,
    link VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_searches_id) REFERENCES user_searches(id) ON DELETE CASCADE
);

CREATE TABLE verification_codes (
    email VARCHAR(255) PRIMARY KEY,
    verification_code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL
);
