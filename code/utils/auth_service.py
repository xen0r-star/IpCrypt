import os
from pathlib import Path

from argon2 import PasswordHasher, Type, exceptions
from dotenv import load_dotenv
from psycopg import connect, OperationalError
from psycopg.rows import dict_row

# .env à la racine du projet (IpCrypt/.env), à deux niveaux au-dessus de ce fichier.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# ══════════════════════════════════════════════
# Logique métier
# ══════════════════════════════════════════════

# time_cost=16 et memory_cost=64 Mo rendent les attaques GPU non-viables.
pwdHasher = PasswordHasher(
    time_cost=16,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    salt_len=32,
    encoding="utf-8",
    type=Type.ID
)

_connection = None


def _open_connection():
    host = os.getenv("DB_HOST")
    password = os.getenv("DB_PASSWORD")
    if not host or not password:
        raise ValueError("DB_HOST et DB_PASSWORD doivent etre definis dans les variables d'environnement (.env).")
    return connect(
        host=host,
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=password,
        sslmode=os.getenv("DB_SSLMODE", "require"),
        row_factory=dict_row,
        autocommit=True,
        connect_timeout=10,
    )


def get_connection():
    """Retourne la connexion persistante, en la recréant si elle est fermée ou cassée."""
    global _connection
    if _connection is None or _connection.closed:
        _connection = _open_connection()
    return _connection


def _run(op):
    """Exécute op(cursor), avec une reconnexion automatique en cas d'erreur réseau."""
    global _connection
    try:
        with get_connection().cursor() as cur:
            return op(cur)
    except OperationalError:
        _connection = None
        with get_connection().cursor() as cur:
            return op(cur)


def recuperation_motDePasse_database(username):
    """Retourne la ligne utilisateur (user_id, username, password, is_admin, is_firstconnexion) ou None si inexistant."""
    def op(cur):
        cur.execute(
            "SELECT user_id, username, password, is_admin, is_firstconnexion FROM users WHERE username=%s",
            (username,),
        )
        return cur.fetchone()
    return _run(op)


def recuperation_utilisateur_database(username):
    """Alias de recuperation_motDePasse_database."""
    return recuperation_motDePasse_database(username)


def ecrire_audit(cur, table_name: str, operation: str, record_id, user_id: int, details: str = None) -> None:
    """Ajoute une ligne au journal audit_log (tag = numéro d'employé). À appeler dans la même transaction que la modification."""
    if user_id is None:
        raise ValueError("Le numéro d'employé est obligatoire pour tagger une modification.")
    cur.execute(
        "INSERT INTO audit_log (table_name, operation, record_id, user_id, details) VALUES (%s, %s, %s, %s, %s)",
        (table_name, operation, str(record_id), user_id, details),
    )


def inscription_dans_database(username: str, profilUser: str, passwordHashed: str, acteur_id: int) -> bool:
    """Insère un nouvel utilisateur et tague l'opération avec l'admin qui l'a créé. Lève UniqueViolation si le nom est pris."""
    def op(cur):
        with cur.connection.transaction():
            cur.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s) RETURNING user_id",
                (username, passwordHashed, profilUser == "Admin"),
            )
            nouveau_id = cur.fetchone()["user_id"]
            ecrire_audit(cur, "users", "INSERT", nouveau_id, acteur_id,
                         f"Création du compte '{username}' (profil {profilUser})")
        return True
    return _run(op)


def update_motDePasse_premiere_connexion_database(username: str, passwordHashed: str) -> bool:
    """Met à jour le mot de passe, bascule is_firstconnexion à FALSE et tague l'opération. Retourne False si introuvable."""
    def op(cur):
        with cur.connection.transaction():
            cur.execute(
                "UPDATE users SET password=%s, is_firstconnexion=FALSE WHERE username=%s RETURNING user_id",
                (passwordHashed, username),
            )
            ligne = cur.fetchone()
            if ligne is None:
                return False
            ecrire_audit(cur, "users", "UPDATE", ligne["user_id"], ligne["user_id"],
                         "Changement du mot de passe obligatoire (première connexion ou réinitialisation globale)")
            return True
    return _run(op)


def verification_motDePasse(passwordToVerify: str, passwordHashed: str) -> bool:
    """Vérifie un mot de passe en clair contre un hash Argon2 stocké en base."""
    try:
        # verify(stored_hash, plain_password) — ordre contre-intuitif imposé par argon2-cffi.
        pwdHasher.verify(passwordHashed, passwordToVerify)
        return True
    except exceptions.VerifyMismatchError:
        return False
    except exceptions.VerificationError:
        return False
    except Exception:
        return False


def hashage_motDePasse(motDePasseEnClaire: str, source: str, username: str, profilUser: str = None, acteur_id: int = None) -> bool:
    """
    Point d'entrée unique pour toutes les opérations sur les mots de passe.
      - connexion_ui       : vérifie le mot de passe contre le hash stocké.
      - inscription_ui     : hache le mot de passe et insère le nouvel utilisateur.
      - first_connexion_ui : hache le mot de passe et met à jour le compte existant.
    Toute exception est avalée et retourne False pour ne pas exposer les détails d'erreur.
    """
    try:
        if source == "connexion_ui":
            motDePasseAVerifier = recuperation_motDePasse_database(username)
            if motDePasseAVerifier is None:
                return False
            passwordHash = motDePasseAVerifier.get('password', '')
            return verification_motDePasse(motDePasseEnClaire, passwordHash)

        elif source == "inscription_ui":
            motDePasseHashe = pwdHasher.hash(motDePasseEnClaire)
            return inscription_dans_database(username, profilUser, motDePasseHashe, acteur_id)

        elif source == "first_connexion_ui":
            motDePasseHashe = pwdHasher.hash(motDePasseEnClaire)
            return update_motDePasse_premiere_connexion_database(username, motDePasseHashe)

        else:
            return False
    except Exception:
        return False


def nouveau_mdp_identique_ancien(username: str, nouveau_mdp: str) -> bool:
    """
    True si le nouveau mot de passe est identique à celui actuellement stocké. Indispensable après une réinitialisation
    globale : si la base a été volée, remettre le même mot de passe laisserait le hash volé valable.
    """
    try:
        user = recuperation_motDePasse_database(username)
        return user is not None and verification_motDePasse(nouveau_mdp, user.get("password", ""))
    except Exception:
        return False



# Bouton de réinitialisation globale des mots de passe par les admins
NB_ADMINS_REQUIS_RESET = 2    # nombre d'administrateurs DIFFÉRENTS à réunir
VALIDITE_VOTE_HEURES = 24     # un vote plus ancien est ignoré et supprimé


def etat_reinitialisation_globale() -> list | None:
    """Retourne la liste des noms d'administrateurs ayant voté (votes encore valables), ou None en cas d'erreur."""
    def op(cur):
        cur.execute(
            "SELECT u.username FROM admin_reset_votes v JOIN users u ON u.user_id = v.admin_id "
            f"WHERE v.voted_at > NOW() - INTERVAL '{VALIDITE_VOTE_HEURES} hours' ORDER BY v.voted_at"
        )
        return [ligne["username"] for ligne in cur.fetchall()]
    try:
        return _run(op)
    except Exception as e:
        print(f"[DB] etat_reinitialisation_globale ERREUR {type(e).__name__}: {e}")
        return None


def a_deja_vote_reinitialisation(user_id: int) -> bool:
    """True si l'administrateur user_id a un vote encore valable."""
    def op(cur):
        cur.execute(
            "SELECT admin_id FROM admin_reset_votes "
            f"WHERE admin_id=%s AND voted_at > NOW() - INTERVAL '{VALIDITE_VOTE_HEURES} hours'",
            (user_id,),
        )
        return cur.fetchone() is not None
    try:
        return _run(op)
    except Exception as e:
        print(f"[DB] a_deja_vote_reinitialisation ERREUR {type(e).__name__}: {e}")
        return False


def voter_reinitialisation_globale(user_id: int) -> dict:
    """
    Enregistre le vote de l'administrateur user_id. Dès que NB_ADMINS_REQUIS_RESET administrateurs différents ont voté,
    tous les comptes sont repassés en changement de mot de passe obligatoire et les votes sont effacés.
    Retourne {'statut': ..., 'votes': [noms]} avec statut parmi : refuse, deja_vote, en_attente, declenche, erreur.
    """
    def op(cur):
        with cur.connection.transaction():
            # Le contrôle admin est refait ici côté base : on ne se fie pas au bouton affiché par l'interface.
            cur.execute("SELECT is_admin FROM users WHERE user_id=%s", (user_id,))
            ligne = cur.fetchone()
            if ligne is None or not ligne["is_admin"]:
                return {"statut": "refuse", "votes": []}

            # Verrou : deux admins qui cliquent en même temps ne doivent pas se rater (chacun ne verrait que son vote).
            cur.execute("LOCK TABLE admin_reset_votes IN SHARE ROW EXCLUSIVE MODE")
            cur.execute(f"DELETE FROM admin_reset_votes WHERE voted_at <= NOW() - INTERVAL '{VALIDITE_VOTE_HEURES} hours'")
            cur.execute(
                "INSERT INTO admin_reset_votes (admin_id) VALUES (%s) ON CONFLICT (admin_id) DO NOTHING RETURNING admin_id",
                (user_id,),
            )
            nouveau_vote = cur.fetchone() is not None
            if nouveau_vote:
                ecrire_audit(cur, "admin_reset_votes", "INSERT", user_id, user_id,
                             "Vote pour la réinitialisation globale des mots de passe")

            cur.execute(
                "SELECT u.username FROM admin_reset_votes v JOIN users u ON u.user_id = v.admin_id ORDER BY v.voted_at"
            )
            votants = [r["username"] for r in cur.fetchall()]

            if len(votants) >= NB_ADMINS_REQUIS_RESET:
                cur.execute("UPDATE users SET is_firstconnexion = TRUE")
                nb_comptes = cur.rowcount
                cur.execute("DELETE FROM admin_reset_votes")
                ecrire_audit(cur, "users", "UPDATE", "ALL", user_id,
                             f"Réinitialisation globale des mots de passe ({nb_comptes} comptes), validée par : {', '.join(votants)}")
                return {"statut": "declenche", "votes": votants}

            return {"statut": "en_attente" if nouveau_vote else "deja_vote", "votes": votants}

    try:
        return _run(op)
    except Exception as e:
        print(f"[DB] voter_reinitialisation_globale ERREUR {type(e).__name__}: {e}")
        return {"statut": "erreur", "votes": []}


def annuler_vote_reinitialisation(user_id: int) -> bool:
    """Retire le vote de l'administrateur user_id (clic par erreur). Retourne True si un vote a été retiré."""
    def op(cur):
        with cur.connection.transaction():
            cur.execute("DELETE FROM admin_reset_votes WHERE admin_id=%s RETURNING admin_id", (user_id,))
            if cur.fetchone() is None:
                return False
            ecrire_audit(cur, "admin_reset_votes", "DELETE", user_id, user_id,
                         "Annulation du vote pour la réinitialisation globale des mots de passe")
            return True
    try:
        return _run(op)
    except Exception as e:
        print(f"[DB] annuler_vote_reinitialisation ERREUR {type(e).__name__}: {e}")
        return False
