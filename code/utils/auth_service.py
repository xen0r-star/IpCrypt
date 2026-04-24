import os

from argon2 import PasswordHasher, Type, exceptions
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

#parametre argon2 - hésite a les mettres dans .venv (variable d'environnement pour plus sécutité)
pwdHasher = PasswordHasher(
    time_cost=16,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    salt_len=32,
    encoding="utf-8",
    type=Type.ID
)

def get_connection():
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
    )

#il faut une fonction qui va aller vérif dans le db grace au nom d'utilisateur si les mdp correspondent ou pas
def recuperation_motDePasse_database(username):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT username, password, is_admin, is_firstconnexion FROM users WHERE username=%s"
            cursor.execute(sql, (username,))
            return cursor.fetchone()


def recuperation_utilisateur_database(username):
    return recuperation_motDePasse_database(username)

def inscription_dans_database(username:str, profilUser:str, passwordHashed:str) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)"
            is_admin = profilUser == "Admin"
            cursor.execute(sql, (username, passwordHashed, is_admin))
        connection.commit()
    return True


def update_motDePasse_premiere_connexion_database(username: str, passwordHashed: str) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET password=%s, is_firstconnexion=FALSE WHERE username=%s"
            cursor.execute(sql, (passwordHashed, username))
            updated_rows = cursor.rowcount
        connection.commit()
    return updated_rows == 1

#verification du mot de passe 
def verification_motDePasse(passwordToVerify: str, passwordHashed: str) -> bool:
    try:
        # Argon2 verify signature: verify(stored_hash, plain_password)
        pwdHasher.verify(passwordHashed, passwordToVerify)
        return True
    except exceptions.VerifyMismatchError:
        return False
    except exceptions.VerificationError:
        return False
    except Exception:
        return False

#hashage du mot de passe et en fonction de la source on vérifie ou on enregistre
def hashage_motDePasse(motDePasseEnClaire: str, source: str, username: str, profilUser: str = None) -> bool:
    try:
        if source == "connexion_ui":
            # Connexion: ne pas re-hasher; verifier le password en clair contre le hash stocke.
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