import tkinter as tk
import ctypes
from pathlib import Path
from PIL import Image, ImageTk

# Icône barre des tâches Windows — AVANT tout import tkinter/ctk
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("IpCrypt.NetworkTool.1.0")

BASE = Path(__file__).resolve().parent
ICO  = BASE / "images" / "menuIpCrypt.ico"
PNG  = BASE / "images" / "menuIpCrypt.png"
ICO2 = BASE / "images" / "iconeIpCrypt.ico"

def show_splash() -> tk.Tk:
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

    after_id = None  # track the callback

    def animate_dots(count=0):
        nonlocal after_id
        dots_label.config(text="Chargement" + "." * count)
        after_id = splash.after(400, animate_dots, (count + 1) % 4)

    animate_dots()
    splash._dots_after_id = lambda: after_id  # expose pour annulation
    splash.update()
    return splash

def launch(splash: tk.Tk) -> None:
    # imports lourds ici — CTk, PIL, etc. chargés pendant que le splash est visible
    from screens.login_screen      import create_connexion_ui
    from screens.register_screen   import create_inscription_ui
    from screens.menu_screen       import create_menu_ui
    from screens.subnet_inspector  import create_ip_verification_ui
    from screens.network_comparator import create_ip_association_ui
    from screens.cidr_explorer     import create_cidr_table_ui
    from utils.auth_service        import hashage_motDePasse
    from tkinter import messagebox

    try:
        for after_id in splash.tk.call("after", "info"):
            splash.after_cancel(after_id)
    except Exception:
        pass
    splash.destroy()

    current_is_admin = False

    # si dessous on retrouve chaque appel aux fonctions pour l'ouverture des pages
    def on_login_success(username=None, password=None, is_admin=None):
        """Callback pour la connexion: hache et vérifie le mot de passe"""
        if not username or not password:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe manquant")
            return
        
        if hashage_motDePasse(password, "connexion_ui", username):
            open_menu(is_admin=is_admin, username=username)
        else:
            messagebox.showerror("Erreur d'authentification", "Nom d'utilisateur ou mot de passe incorrect")

    def on_signup_success(username=None, password=None, profile=None):
        """Callback pour l'inscription: hache et enregistre le mot de passe"""
        if not username or not password or not profile:
            messagebox.showerror("Erreur", "Données d'inscription incomplètes")
            return
        
        if hashage_motDePasse(password, "inscription_ui", username, profile):
            messagebox.showinfo("Succès", "Compte créé avec succès!")
            is_admin = (profile == "Admin")
            open_menu(is_admin=is_admin, username=username)
        else:
            messagebox.showerror("Erreur", "Erreur lors de la création du compte")

    def open_connexion() -> None:
        #Affiche la page de connexion
        #verifie que le login est correcte
        create_connexion_ui(
            on_login_success=on_login_success,
            on_go_to_signup=None,
        )

    def open_inscription(from_menu: bool = False):
        back_callback = open_menu if from_menu else open_connexion
        back_text     = "Retour menu" if from_menu else "Connexion"
        create_inscription_ui(on_signup_success=on_signup_success, on_back=back_callback, back_button_text=back_text)

    def open_menu(is_admin=None, username=None):
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

    def open_ip_verification(): create_ip_verification_ui(on_back=open_menu)
    def open_ip_association():  create_ip_association_ui(on_back=open_menu)
    def open_cidr_table():      create_cidr_table_ui(on_back=open_menu)

    open_connexion()

if __name__ == "__main__":
    splash = show_splash()
    splash.after(1500, lambda: launch(splash))
    splash.mainloop()