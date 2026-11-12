"""
Stockage SQLite 3 des découpes en sous-réseaux (fonctionnalité 6).

On ne stocke que les ENTRÉES de la découpe (réseau de base, CIDR de base, nombre de sous-réseaux demandés)
et le dernier modificateur (numéro d'employé + date) : le résultat de la découpe n'est jamais stocké.
Le fichier de base est créé automatiquement au premier usage (module sqlite3 de Python, rien à installer).
"""
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

CHEMIN_PAR_DEFAUT = Path(__file__).resolve().parent.parent / "database" / "decoupes.sqlite3"
FORMAT_DATE = "%Y-%m-%d %H:%M:%S"


def chemin_base() -> Path:
    """Chemin du fichier SQLite : variable d'environnement SQLITE_PATH (.env) ou code/database/decoupes.sqlite3."""
    return Path(os.getenv("SQLITE_PATH") or CHEMIN_PAR_DEFAUT)


def _connexion() -> sqlite3.Connection:
    """Ouvre la base (la crée avec sa table si besoin). Les lignes sont lisibles par nom de colonne."""
    chemin = chemin_base()
    chemin.parent.mkdir(parents=True, exist_ok=True)
    connexion = sqlite3.connect(chemin)
    connexion.row_factory = sqlite3.Row
    connexion.execute(
        "CREATE TABLE IF NOT EXISTS subnet_splits ("
        "split_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "network_address TEXT NOT NULL, "
        "base_cidr INTEGER NOT NULL, "
        "requested_subnets INTEGER NOT NULL, "
        "last_modified_by INTEGER NOT NULL, "
        "last_modified_at TEXT NOT NULL, "
        "UNIQUE (network_address, base_cidr, requested_subnets))"
    )
    return connexion


def enregistrer(adresse_reseau: str, cidr_base: int, nb_sous_reseaux: int, user_id: int, record_id=None) -> tuple:
    """
    Enregistre une découpe et retourne (opération, id de la ligne, détails) pour le journal d'audit.
    1) mêmes valeurs déjà en base : pas de doublon, on met à jour le dernier modificateur ;
    2) enregistrement rechargé depuis l'historique (record_id) : on le modifie ;
    3) sinon : nouvel enregistrement.
    """
    details = f"network_address={adresse_reseau}, base_cidr={cidr_base}, requested_subnets={nb_sous_reseaux}"
    maintenant = datetime.now().strftime(FORMAT_DATE)

    with closing(_connexion()) as connexion:
        with connexion:  # une seule transaction : validée si tout va bien, annulée sinon
            identique = connexion.execute(
                "SELECT split_id FROM subnet_splits WHERE network_address=? AND base_cidr=? AND requested_subnets=?",
                (adresse_reseau, cidr_base, nb_sous_reseaux),
            ).fetchone()
            if identique is not None:
                connexion.execute("UPDATE subnet_splits SET last_modified_by=?, last_modified_at=? WHERE split_id=?",
                                  (user_id, maintenant, identique["split_id"]))
                return "UPDATE", identique["split_id"], details

            if record_id is not None:
                ancien = connexion.execute(
                    "SELECT network_address, base_cidr, requested_subnets FROM subnet_splits WHERE split_id=?",
                    (record_id,),
                ).fetchone()
                if ancien is not None:
                    connexion.execute(
                        "UPDATE subnet_splits SET network_address=?, base_cidr=?, requested_subnets=?, "
                        "last_modified_by=?, last_modified_at=? WHERE split_id=?",
                        (adresse_reseau, cidr_base, nb_sous_reseaux, user_id, maintenant, record_id),
                    )
                    return "UPDATE", record_id, (
                        f"avant : network_address={ancien['network_address']}, base_cidr={ancien['base_cidr']}, "
                        f"requested_subnets={ancien['requested_subnets']} -> après : {details}"
                    )

            curseur = connexion.execute(
                "INSERT INTO subnet_splits (network_address, base_cidr, requested_subnets, last_modified_by, last_modified_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (adresse_reseau, cidr_base, nb_sous_reseaux, user_id, maintenant),
            )
            return "INSERT", curseur.lastrowid, details


def lister(limite: int) -> list:
    """
    Historique des découpes, de la plus récente à la plus ancienne :
    [{'id', 'reseau', 'cidr', 'nb_sous_reseaux', 'modifie_par_id', 'modifie_le' (datetime)}, ...].
    """
    with closing(_connexion()) as connexion:
        lignes = connexion.execute(
            "SELECT split_id, network_address, base_cidr, requested_subnets, last_modified_by, last_modified_at "
            "FROM subnet_splits ORDER BY last_modified_at DESC, split_id DESC LIMIT ?",
            (limite,),
        ).fetchall()
    return [
        {
            "id": ligne["split_id"],
            "reseau": ligne["network_address"],
            "cidr": ligne["base_cidr"],
            "nb_sous_reseaux": ligne["requested_subnets"],
            "modifie_par_id": ligne["last_modified_by"],
            "modifie_le": datetime.strptime(ligne["last_modified_at"], FORMAT_DATE),
        }
        for ligne in lignes
    ]
