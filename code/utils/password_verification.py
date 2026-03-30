from argon2 import PasswordHasher, exceptions
from argon2 import Type

from UI.connexion_ui import create_connexion_ui
from UI.inscription_ui import submit_inscription

import pymysql.cursors

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

#meme raisonnement que pour les parametres 'argon2
#etant donné que se sont des info sensible les décaller dans .venv
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='gestion_ip',
    cursorclass=pymysql.cursors.DictCursor
)

#il faut une fonction qui va aller vérif dans le db grace au nom d'utilisateur si les mdp correspondent ou pas
def recuperation_motDePasse_database(username):
    with connection:
        with connection.cursor() as cursor:
            #requete pour recuperer le mot hashé et faire une comparaison
            sql = "SELECT password FROM users WHERE username=%s"
            cursor.execute(sql, (username))
            result = cursor.fetchone()
            print(result)
            return result

def inscription_dans_database(username:str, profilUser:str, passwordHashed:str) -> bool:
    with connection:
        with connection.cursor() as cursor:
            #insertion des données
            sql = "INSERT INTO users (username, password, isAdmin) VALUES (%s, %s, %s)"
            #changemenent de profil user de str a bool
            if(profilUser == "Admin"):
                profilUser = 1
            else :
                profilUser = 0
            cursor.execute(sql, (username, passwordHashed, profilUser))
            connection.commit()
    print("Ajout effectue")
    return True

#verification du mot de passe 
def verification_motDePasse(passwordToVerify: str, passwordHashed: str) -> bool:
    try:
        pwdHasher.verify(passwordHashed, passwordToVerify)
        print("password correct")
        return True
    except exceptions.VerifyMismatchError:
        print("password incorrect")
        return False
    except exceptions.VerificationError as e:
        print(f"Verification failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}") 
        return False

#hashage du mot de passe et en fonction de la source on vérifie ou on enregistre
def hashage_motDePasse(motDePasseEnClaire: str, source: str, username: str, profilUser: str = None) -> bool:
    try:
        if source == "connexion_ui":
            # Connexion: hash le mot de passe et le vérifie contre la BD
            motDePasseHashe = pwdHasher.hash(motDePasseEnClaire)
            motDePasseAVerifier = recuperation_motDePasse_database(username)
            if motDePasseAVerifier is None:
                print("Utilisateur non trouvé")
                return False
            # Récupérer le hash depuis le dictionnaire
            passwordHash = motDePasseAVerifier.get('password', '')
            return verification_motDePasse(motDePasseHashe, passwordHash)
        
        elif source == "inscription_ui":
            # Inscription: hash et enregistre dans la BD
            motDePasseHashe = pwdHasher.hash(motDePasseEnClaire)
            return inscription_dans_database(username, profilUser, motDePasseHashe)
        
        else:
            print(f"Source inconnue: {source}")
            return False
    except Exception as e:
        print(f"Error hashing password: {e}")
        return False