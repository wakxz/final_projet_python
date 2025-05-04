-- Création de la base de données
CREATE DATABASE IF NOT EXISTS gestion_excuses;
USE gestion_excuses;

-- Création de la table `etudiants`
CREATE TABLE IF NOT EXISTS etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    date_inscription DATE NOT NULL
);

-- Création de la table `excuses`
CREATE TABLE IF NOT EXISTS excuses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    excuse TEXT NOT NULL,
    date_excuse DATE NOT NULL,
    note_excuse FLOAT,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE
);

-- Création de l'utilisateur s'il n'existe pas (mot de passe = 123)
CREATE USER IF NOT EXISTS 'etudiant'@'localhost' IDENTIFIED BY '123';

-- Donner tous les droits sur la base gestion_excuses
GRANT ALL PRIVILEGES ON gestion_excuses.* TO 'etudiant'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;
