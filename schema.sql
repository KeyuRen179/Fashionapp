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
    image_1 VARCHAR(1000),
    image_2 VARCHAR(1000),
    image_3 VARCHAR(1000),
    image_4 VARCHAR(1000),
    image_5 VARCHAR(1000),
    image_6 VARCHAR(1000),
    web_link_1 VARCHAR(255),
    web_link_2 VARCHAR(255),
    web_link_3 VARCHAR(255),
    web_link_4 VARCHAR(255),
    web_link_5 VARCHAR(255),
    web_link_6 VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Adding a User History Form
CREATE TABLE user_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    poem TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
