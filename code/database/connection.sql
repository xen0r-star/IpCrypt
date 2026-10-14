-- =====================================================================
-- Base de données SQLite 3 : stockage uniquement
-- IMPORTANT : exécuter PRAGMA foreign_keys = ON à CHAQUE connexion Python
--             (SQLite ne vérifie pas les clés étrangères par défaut)
-- =====================================================================
PRAGMA foreign_keys = ON;

-- Utilisateurs (user_id sert de numéro d'employé pour le tagging)
CREATE TABLE IF NOT EXISTS users (
    user_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    username          VARCHAR(50) NOT NULL UNIQUE,
    password          TEXT NOT NULL,
    is_admin          INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0,1)),
    is_firstConnexion INTEGER NOT NULL DEFAULT 1 CHECK (is_firstConnexion IN (0,1))
);

INSERT INTO users (username, password, is_admin, is_firstConnexion)
VALUES
    ('client_test',   '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', 0, 0),
    ('client_test_2', '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', 0, 1),
    ('client_test_3', '$argon2id$v=19$m=65536,t=3,p=4$+GkIxD3Z1AXdgztOxiLBQg$6WK+Ku14fVXROPGX4AFXMyHvcDNnjkfZEYrW+YDs3WM', 1, 0)
ON CONFLICT (username) DO NOTHING;

-- Fonctionnalité 1 : masques /8 à /30 (résultat stocké)
CREATE TABLE IF NOT EXISTS masks (
    cidr         INTEGER PRIMARY KEY CHECK (cidr BETWEEN 8 AND 30),
    mask_binary  VARCHAR(35) NOT NULL,
    mask_decimal VARCHAR(15) NOT NULL
);

-- Fonctionnalité 2 : format d'une IP (entrée brute, peut être invalide)
CREATE TABLE IF NOT EXISTS ip_format_checks (
    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip       VARCHAR(45) NOT NULL
);

-- Fonctionnalité 3 : classe d'une IP (entrée)
CREATE TABLE IF NOT EXISTS ip_class_checks (
    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip       VARCHAR(15) NOT NULL
);

-- Fonctionnalité 4 : masque de classe (entrée)
CREATE TABLE IF NOT EXISTS ip_class_mask_checks (
    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip       VARCHAR(15) NOT NULL
);

-- Fonctionnalité 5 : réseau / sous-réseau (entrées + dernier modificateur)
CREATE TABLE IF NOT EXISTS network_calculations (
    calc_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address       VARCHAR(15) NOT NULL,
    subnet_mask      VARCHAR(15) NOT NULL,
    last_modified_by INTEGER NOT NULL REFERENCES users(user_id),
    last_modified_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Fonctionnalité 6 : même réseau ? (entrées + dernier modificateur)
CREATE TABLE IF NOT EXISTS same_network_checks (
    check_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ip1              VARCHAR(15) NOT NULL,
    mask1            VARCHAR(15) NOT NULL,
    ip2              VARCHAR(15) NOT NULL,
    mask2            VARCHAR(15) NOT NULL,
    last_modified_by INTEGER NOT NULL REFERENCES users(user_id),
    last_modified_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Nouvelle fonctionnalité : découpe en sous-réseaux (résultats stockés)
CREATE TABLE IF NOT EXISTS subnet_splits (
    split_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    network_address   VARCHAR(15) NOT NULL,
    base_cidr         INTEGER NOT NULL,
    requested_subnets INTEGER NOT NULL,
    bits_borrowed     INTEGER NOT NULL,
    new_cidr          INTEGER NOT NULL,
    obtained_subnets  INTEGER NOT NULL,
    hosts_per_subnet  INTEGER NOT NULL,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS subnet_split_details (
    detail_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    split_id        INTEGER NOT NULL REFERENCES subnet_splits(split_id) ON DELETE CASCADE,
    subnet_number   INTEGER NOT NULL,
    network_address VARCHAR(15) NOT NULL,
    first_host      VARCHAR(15) NOT NULL,
    last_host       VARCHAR(15) NOT NULL,
    broadcast       VARCHAR(15) NOT NULL,
    UNIQUE (split_id, subnet_number)
);

-- Journal des modifications (tagging), rempli par l'application
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    operation  VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
    record_id  VARCHAR(50),
    user_id    INTEGER NOT NULL REFERENCES users(user_id),
    changed_at TEXT NOT NULL DEFAULT (datetime('now')),
    details    TEXT
);