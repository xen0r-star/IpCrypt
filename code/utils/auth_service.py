import os

from argon2 import PasswordHasher, Type, exceptions
from dotenv import load_dotenv
from psycopg import connect, OperationalError
from psycopg.rows import dict_row

load_dotenv()

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
    """Retourne la ligne utilisateur (username, password, is_admin, is_firstconnexion) ou None si inexistant."""
    def op(cur):
        cur.execute(
            "SELECT username, password, is_admin, is_firstconnexion FROM users WHERE username=%s",
            (username,),
        )
        return cur.fetchone()
    return _run(op)


def recuperation_utilisateur_database(username):
    """Alias de recuperation_motDePasse_database."""
    return recuperation_motDePasse_database(username)


def inscription_dans_database(username: str, profilUser: str, passwordHashed: str) -> bool:
    """Insère un nouvel utilisateur en base. Lève UniqueViolation si le nom d'utilisateur est déjà pris."""
    def op(cur):
        cur.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
            (username, passwordHashed, profilUser == "Admin"),
        )
        return True
    return _run(op)


def update_motDePasse_premiere_connexion_database(username: str, passwordHashed: str) -> bool:
    """Met à jour le mot de passe et bascule is_firstconnexion à FALSE. Retourne False si l'utilisateur est introuvable."""
    def op(cur):
        cur.execute(
            "UPDATE users SET password=%s, is_firstconnexion=FALSE WHERE username=%s",
            (passwordHashed, username),
        )
        return cur.rowcount == 1
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


def hashage_motDePasse(motDePasseEnClaire: str, source: str, username: str, profilUser: str = None) -> bool:
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
            return inscription_dans_database(username, profilUser, motDePasseHashe)

        elif source == "first_connexion_ui":
            motDePasseHashe = pwdHasher.hash(motDePasseEnClaire)
            return update_motDePasse_premiere_connexion_database(username, motDePasseHashe)

        else:
            return False
    except Exception:
        return False
