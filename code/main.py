"""Point d'entree unique de l'application UI.

Ce module orchestre la navigation entre ecrans:
- Connexion
- Menu principal
- Modules (verification, association, table CIDR, inscription)

La logique de routage est centralisee ici pour garder les ecrans UI simples
et focalises sur leur rendu.
"""
#on import les fonctions qui cree les interfaces de chaque ecran. Chaque fonction prend un callback on_back"""
from UI.connexion_ui import create_connexion_ui
from UI.inscription_ui import create_inscription_ui
from UI.menu_ui import create_menu_ui
from UI.ip_verification_ui import create_ip_verification_ui
from UI.ip_association_ui import create_ip_association_ui
from UI.cidr_table_ui import create_cidr_table_ui

#Demarre l'application
def run_app() -> None:
    
    #current_is_admin est une varibale placé a false dés le depart et qui permet en fonction de 
    #la connection de montrer le menu inscription ou pas dans le menu
    current_is_admin = False

    # si dessous on retrouve chaque appel aux fonctions pour l'ouverture des pages
    def open_connexion() -> None:
        #Affiche la page de connexion
        #verifie que le login est correcte
        create_connexion_ui(
            on_login_success=open_menu,
        )

    def open_inscription(from_menu: bool = False) -> None:
        #Affiche l'ecran d'inscription avec un retour contextuel.

        #Depuis la connexion: le bouton retour renvoie vers Connexion.
        #Depuis le menu: le bouton retour renvoie vers Menu.

        back_callback = open_menu if from_menu else open_connexion
        back_text = "Retour menu" if from_menu else "Connexion"

        create_inscription_ui(
            on_signup_success=open_menu,
            on_back=back_callback,
            back_button_text=back_text,
        )

    def open_menu(is_admin=None, username=None) -> None:
        #Affiche le menu principal en fonction du role utilisateur.

        #Le callback de connexion transmet is_admin. On le memorise pour que
        #les retours depuis les modules rechargent le bon menu sans recalcul.
        
        nonlocal current_is_admin
        if is_admin is not None:
            current_is_admin = is_admin

        create_menu_ui(
            on_open_ip_verification=open_ip_verification,
            on_open_ip_association=open_ip_association,
            on_open_inscription=lambda: open_inscription(from_menu=True),
            on_open_cidr_table=open_cidr_table,
            on_logout=open_connexion,
            is_admin=current_is_admin,
        )

    def open_ip_verification() -> None:
        #Ouvre le module de verification IP.

        create_ip_verification_ui(on_back=open_menu)

    def open_ip_association() -> None:
        #Ouvre le module d'association IP.

        create_ip_association_ui(on_back=open_menu)

    def open_cidr_table() -> None:
        #Ouvre le module de table CIDR.

        create_cidr_table_ui(on_back=open_menu)

    # La connexion est toujours l'ecran initial.
    open_connexion()

if __name__ == "__main__":
    run_app()