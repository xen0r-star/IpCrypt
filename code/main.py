import tkinter as tk
import ctypes
from pathlib import Path
from PIL import Image, ImageTk

# Icône barre des tâches Windows — doit être défini AVANT tout import tkinter/ctk.
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("IpCrypt.NetworkTool.1.0")

BASE = Path(__file__).resolve().parent
ICO  = BASE / "images" / "iconeIpCrypt.ico"
PNG  = BASE / "images" / "menuIpCrypt.png"


def show_splash() -> tk.Tk:
    """Affiche le splash screen animé pendant le chargement des modules lourds."""
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.configure(bg="#ffffff")

    if ICO.exists():
        splash.iconbitmap(str(ICO))

    pil_img = Image.open(str(PNG)).resize((550, 300), Image.LANCZOS)
    w, h = pil_img.size
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    splash.geometry(f"{w}x{h + 40}+{(sw-w)//2}+{(sh-h)//2}")

    logo_img = ImageTk.PhotoImage(pil_img)
    label = tk.Label(splash, image=logo_img, bd=0, bg="#ffffff")
    label.image = logo_img
    label.pack()

    dots_label = tk.Label(splash, text="Chargement", font=("Segoe UI", 11), bg="#ffffff", fg="#5b6b84")
    dots_label.pack(pady=(4, 0))

    after_id = None

    def animate_dots(count=0):
        """Anime les points de chargement en cycle de 0 à 3."""
        nonlocal after_id
        dots_label.config(text="Chargement" + "." * count)
        after_id = splash.after(400, animate_dots, (count + 1) % 4)

    animate_dots()
    splash._dots_after_id = lambda: after_id
    splash.update()
    return splash


def launch(splash: tk.Tk) -> None:
    """Détruit le splash, importe tous les écrans puis démarre la navigation depuis la connexion."""
    from screens.connexion                          import create_connexion_ui
    from screens.changement_mdp_premiere_inscription import create_first_connection_ui
    from screens.inscription                        import create_inscription_ui
    from screens.menu_principal                     import create_menu_ui
    from screens.ip_association                     import create_ip_association_ui
    from screens.gestion_adresse_ip                 import create_menu_ip_ui
    from screens.ip_verification                    import create_ip_verification_ui
    from screens.recherche_classe_ip                import create_definer_class_ui
    from screens.recherche_masque_ip                import create_get_mask_ui
    from screens.definir_reseau_sous_reseau         import create_get_network_ui
    from screens.tableau_cidr                       import create_cidr_table_ui
    from utils.auth_service             import hashage_motDePasse, recuperation_utilisateur_database
    from tkinter import messagebox

    try:
        for after_id in splash.tk.call("after", "info"):
            splash.after_cancel(after_id)
    except Exception:
        pass
    splash.destroy()

    current_is_admin = False

    def on_login_success(username=None, password=None, is_admin=None):
        """Vérifie les identifiants ; redirige vers la première connexion ou le menu selon le flag en base."""
        print(f"[LOGIN] username={username!r}")
        if not username or not password:
            print("[LOGIN] champ vide")
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe manquant")
            return

        try:
            user = recuperation_utilisateur_database(username)
        except Exception as e:
            print(f"[LOGIN] EXCEPTION DB: {type(e).__name__}: {e}")
            messagebox.showerror("Erreur DB", f"{type(e).__name__}: {e}")
            return
        print(f"[LOGIN] user={user!r}")
        if user is None:
            print("[LOGIN] user introuvable en DB")
            messagebox.showerror("Erreur d'authentification", "Nom d'utilisateur ou mot de passe incorrect")
            return

        from utils.auth_service import verification_motDePasse
        verify_ok = verification_motDePasse(password, user.get("password", ""))
        print(f"[LOGIN] verify_ok={verify_ok}")
        if not verify_ok:
            messagebox.showerror("Erreur d'authentification", "Nom d'utilisateur ou mot de passe incorrect")
            return

        db_is_admin = bool(user.get("is_admin"))
        is_first_connexion = bool(user.get("is_firstconnexion"))
        print(f"[LOGIN] is_admin={db_is_admin} is_first={is_first_connexion}")

        if is_first_connexion:
            open_first_connexion(username=username, is_admin=db_is_admin)
        else:
            open_menu(is_admin=db_is_admin, username=username)

    def on_first_connexion_success(username=None, new_password=None, is_admin=False):
        """Met à jour le mot de passe en base puis ouvre le menu."""
        if not username or not new_password:
            messagebox.showerror("Erreur", "Donnees de changement de mot de passe incompletes")
            return

        if hashage_motDePasse(new_password, "first_connexion_ui", username):
            messagebox.showinfo("Succes", "Mot de passe modifie avec succes.")
            open_menu(is_admin=is_admin, username=username)
        else:
            messagebox.showerror("Erreur", "Impossible de modifier le mot de passe.")

    def open_connexion() -> None:
        """Ouvre l'écran de connexion."""
        create_connexion_ui(
            on_login_success=on_login_success,
            on_go_to_signup=None,
        )

    def open_inscription(from_menu: bool = False):
        """Ouvre l'écran d'inscription ; le bouton retour pointe vers le menu si from_menu=True, sinon vers la connexion."""
        back_callback = open_menu if from_menu else open_connexion
        back_text     = "Retour menu" if from_menu else "Connexion"

        def after_signup(username=None, password=None, profile=None):
            """Insère le nouvel utilisateur en base, puis rouvre l'écran d'inscription pour un autre ajout."""
            if not username or not password or not profile:
                messagebox.showerror("Erreur", "Données d'inscription incomplètes")
                return
            if hashage_motDePasse(password, "inscription_ui", username, profile):
                messagebox.showinfo("Succès", "Compte créé avec succès!")
                open_inscription(from_menu=from_menu)
            else:
                messagebox.showerror("Erreur", "Erreur lors de la création du compte")

        create_inscription_ui(on_signup_success=after_signup, on_back=back_callback, back_button_text=back_text)

    def open_first_connexion(username: str, is_admin: bool):
        """Ouvre l'écran de changement de mot de passe obligatoire pour les nouveaux comptes."""
        create_first_connection_ui(
            username=username,
            on_password_changed=lambda username, new_password: on_first_connexion_success(
                username=username,
                new_password=new_password,
                is_admin=is_admin,
            ),
            on_back=open_connexion,
            back_button_text="Annuler",
        )

    def open_menu(is_admin=None, username=None):
        """Ouvre le menu principal en mémorisant le rôle admin pour la session en cours."""
        nonlocal current_is_admin
        if is_admin is not None:
            current_is_admin = is_admin
        create_menu_ui(
            on_open_menu_IP=open_ip_menu,
            on_open_ip_association=open_ip_association,
            on_open_inscription=lambda: open_inscription(from_menu=True),
            on_open_cidr_table=open_cidr_table,
            on_logout=open_connexion,
            is_admin=current_is_admin,
        )

    def open_ip_menu():
        """Ouvre le sous-menu Gestion IP."""
        create_menu_ip_ui(
            on_open_subnet_verification=open_subnet_verification,
            on_open_definer_classe=open_definer_classe,
            on_open_get_mask=open_get_mask,
            on_open_get_network=open_get_network,
            on_back=open_menu,
        )

    def open_ip_association():          create_ip_association_ui(on_back=open_menu)
    def open_cidr_table():              create_cidr_table_ui(on_back=open_menu)
    def open_subnet_verification():     create_ip_verification_ui(on_back=open_ip_menu)
    def open_definer_classe():          create_definer_class_ui(on_back=open_ip_menu)
    def open_get_mask():                create_get_mask_ui(on_back=open_ip_menu)
    def open_get_network():             create_get_network_ui(on_back=open_ip_menu)

    open_connexion()


if __name__ == "__main__":
    splash = show_splash()
    splash.after(1500, lambda: launch(splash))
    splash.mainloop()
