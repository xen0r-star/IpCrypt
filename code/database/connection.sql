-- Utilisateurs (user_id sert de numéro d'employé pour le tagging)
CREATE TABLE IF NOT EXISTS users (
    user_id           INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username          VARCHAR(50) NOT NULL UNIQUE,
    password          TEXT NOT NULL,
    is_admin          BOOLEAN NOT NULL DEFAULT FALSE,
    is_firstConnexion BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO users (username, password, is_admin, is_firstConnexion)
VALUES
    ('client_test',   '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', FALSE, FALSE),
    ('client_test_2', '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', FALSE, TRUE),
    ('client_test_3', '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', TRUE,  FALSE)
ON CONFLICT (username) DO NOTHING;

-- Fonctionnalité 1 : format d'une IP (entrée brute, peut être invalide + RÉSULTAT du contrôle)
CREATE TABLE IF NOT EXISTS ip_format_checks (
    check_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ip       VARCHAR(45) NOT NULL,
    is_valid BOOLEAN NOT NULL
);

-- Fonctionnalité 2 : classe d'une IP (entrée)
CREATE TABLE IF NOT EXISTS ip_class_checks (
    check_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ip       VARCHAR(15) NOT NULL
);

-- Fonctionnalité 3 : masque de classe (entrée)
CREATE TABLE IF NOT EXISTS ip_class_mask_checks (
    check_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ip       VARCHAR(15) NOT NULL
);

-- Fonctionnalité 4 : réseau / sous-réseau (entrées uniquement)
CREATE TABLE IF NOT EXISTS network_calculations (
    calc_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ip_address  VARCHAR(15) NOT NULL,
    subnet_mask VARCHAR(15) NOT NULL
);

-- Fonctionnalité 5 : même réseau ? (entrées + dernier modificateur)
CREATE TABLE IF NOT EXISTS same_network_checks (
    check_id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ip1              VARCHAR(15) NOT NULL,
    mask1            VARCHAR(15) NOT NULL,
    ip2              VARCHAR(15) NOT NULL,
    mask2            VARCHAR(15) NOT NULL,
    last_modified_by INTEGER NOT NULL REFERENCES users(user_id),
    last_modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Fonctionnalité 6 : découpe en sous-réseaux (entrées + dernier modificateur)
CREATE TABLE IF NOT EXISTS subnet_splits (
    split_id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    network_address   VARCHAR(15) NOT NULL,
    base_cidr         INTEGER NOT NULL,
    requested_subnets INTEGER NOT NULL,
    last_modified_by  INTEGER NOT NULL REFERENCES users(user_id),
    last_modified_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Journal des modifications (tagging), rempli par l'application
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation  VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
    record_id  VARCHAR(50),
    user_id    INTEGER NOT NULL REFERENCES users(user_id),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    details    TEXT
);
