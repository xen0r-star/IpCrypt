-- Créer la base de données
CREATE DATABASE IF NOT EXISTS connectionIpCrypt CHARACTER SET = 'utf8mb4';

-- Utiliser la base de données
USE connectionIpCrypt;

-- Créer la table users avec structure optimisée
CREATE TABLE IF NOT EXISTS users (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    isAdmin BOOLEAN NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Exemples d'INSERT
-- Note: Les password sont des hashes Argon2 (ils seront générés en Python lors de l'inscription via argon2)
-- Pour tester en local, tu peux utiliser les hashs d'exemple ci-dessous

INSERT INTO users (username, password, isAdmin) VALUES
('admin', '$argon2id$v=19$m=65540,t=3,p=4$9WcC6Fj2zl8pQkLm3NwOqQ$Vk5V+zE7kB2jL8QmN9pO3U5W6X7Y8Z9a0b1c2d3e4f5g', 1),
('jean', '$argon2id$v=19$m=65540,t=3,p=4$5XyZ1Ab3cDeFgHiJkLmNoP$Pq2R3S4T5U6V7W8X9Y0Z1a2b3c4d5e6f7g8h9i0j1k2l', 0),
('marie', '$argon2id$v=19$m=65540,t=3,p=4$8AbCdEfGhIjKlMnOpQrStU$VwXyZ1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0', 0);

