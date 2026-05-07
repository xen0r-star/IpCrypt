-- PostgreSQL / Supabase script
-- En Supabase, la base est deja creee: ne pas utiliser CREATE DATABASE / USE.

CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_firstConnexion BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);

-- ajout commentaire test webhook
INSERT INTO users (username, password, is_admin, is_firstConnexion) VALUES
('vdp_corentin', '$argon2id$v=19$m=65536,t=3,p=1$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH', TRUE, FALSE),
('cnv_evan', '$argon2id$v=19$m=65536,t=3,p=1$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH', TRUE, FALSE),
('client_test', '$argon2id$v=19$m=65536,t=3,p=1$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH', FALSE, FALSE),
('client_test_2', '$argon2id$v=19$m=65536,t=3,p=1$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH', FALSE, TRUE)
ON CONFLICT (username) DO NOTHING;

DROP TABLE IF EXISTS users; --drop la table
