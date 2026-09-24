CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_firstConnexion BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);

INSERT INTO users (username, password, is_admin, is_firstConnexion) 
VALUES
  ('client_test', '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', FALSE, FALSE),
  ('client_test_2', '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', FALSE, TRUE)
ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, password, is_admin, is_firstConnexion) 
VALUES
  ('client_test_3', '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', TRUE, FALSE)
ON CONFLICT (username) DO NOTHING;
