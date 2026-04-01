-- PostgreSQL / Supabase script
-- En Supabase, la base est deja creee: ne pas utiliser CREATE DATABASE / USE.

CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);

-- Exemples d'INSERT
-- Note: Les password sont des hashes Argon2 (ils seront générés en Python lors de l'inscription via argon2)
-- Pour tester en local, tu peux utiliser les hashs d'exemple ci-dessous

INSERT INTO users (username, password, is_admin) VALUES
('vdp_corentin', '$argon2id$v=19$m=65536,t=3,p=1$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH', TRUE),
('cnv_evan', '$argon2id$v=19$m=65536,t=3,p=1$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH', TRUE),
('client_test', '$argon2id$v=19$m=65536,t=3,p=1$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH', FALSE)
ON CONFLICT (username) DO NOTHING;

