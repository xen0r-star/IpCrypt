from tkinter import BooleanVar, StringVar, messagebox

import customtkinter as ctk

try:
    from utils.auth_policy import validate_password_policy
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from utils.auth_policy import validate_password_policy

from pathlib import Path
ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ancienne couleur - laisse si besoin
# COLORS = {
#     "bg": "#eef1f6",
#     "surface": "#ffffff",
#     "primary": "#3f5fa8",
#     "primary_hover": "#355190",
#     "danger": "#b05f5f",
#     "danger_hover": "#994f4f",
#     "text": "#16233b",
#     "muted": "#5a6b86",
#     "border": "#cfd8e6",
#     "field_bg": "#f6f8fc",
# }

COLORS = {
    "bg": "#f8f9fa",
    "surface": "#ffffff",
    "primary": "#2c5aa0",
    "primary_hover": "#1c4a80",
    "danger": "#a94442",
    "danger_hover": "#8c3a3a",
    "text": "#16233b",
    "muted": "#6a7b86",
    "border": "#e0e0e0",
    "field_bg": "#f6f8fc",
    "panel": "#f6f8fc",
    "success": "#4a8c62",
    "error": "#a94442",
}

def center_window(window: ctk.CTk, width: int, height: int) -> None:
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    pos_x = int((screen_w - width) / 2)
    pos_y = int((screen_h - height) / 2)
    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


def cleanup_window(window: ctk.CTk) -> None:
    """Stop pending Tk callbacks before destroying the window.

    CustomTkinter schedules internal after() jobs (animations / DPI checks).
    Cancelling them avoids 'invalid command name ... (after script)' errors
    during fast window transitions.
    """
    try:
        if window.winfo_exists():
            window.withdraw()
            window.update_idletasks()
    except Exception:
        pass

    try:
        window.quit()
    except Exception:
        pass

    try:
        after_ids = window.tk.call("after", "info")
        if isinstance(after_ids, str):
            after_ids = (after_ids,) if after_ids else ()
        for after_id in after_ids:
            try:
                window.after_cancel(after_id)
            except Exception:
                pass
    except Exception:
        pass
    try:
        if window.winfo_exists():
            window.destroy()
    except Exception:
        # Python 3.14 + CustomTkinter can raise TclError during command cleanup.
        pass


def submit_inscription(entryUserNameInscription, entryPasswordInscription, profile_var):
    username= entryUserNameInscription.get().strip()
    password= entryPasswordInscription.get().strip()
    profile = profile_var.get().strip()

    print(f"Username: {username}, Password: {password}, Profile: {profile}")

def create_inscription_ui(on_signup_success=None, on_back=None, back_button_text="Connexion"):
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("Inscription")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(False, False)
    center_window(app, 600, 520)

    def schedule_navigation(callback, *args, **kwargs):
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=28, pady=20)

    ctk.CTkLabel(
        container,
        text="Inscription",
        font=("Segoe UI", 34, "bold"),
        text_color=COLORS["text"],
    ).pack(anchor="center")

    ctk.CTkLabel(
        container,
        text="Crée un compte utilisateur",
        font=("Segoe UI", 15),
        text_color=COLORS["muted"],
    ).pack(anchor="center", pady=(4, 16))

    card = ctk.CTkFrame(
        container,
        fg_color=COLORS["surface"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=14,
    )
    card.pack(fill="x")

    form = ctk.CTkFrame(card, fg_color="transparent")
    form.pack(fill="x", padx=20, pady=18)

    ctk.CTkLabel(form, text="Nom utilisateur", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
    entryUserNameInscription = ctk.CTkEntry(
        form,
        height=40,
        fg_color=COLORS["field_bg"],
        border_color=COLORS["border"],
        placeholder_text="Ex. : jean_dupont (min. 3 caractères)",
    )
    entryUserNameInscription.pack(fill="x", pady=(6, 12))

    # Insérer une commande pour récupérer si admin ou client.
    ctk.CTkLabel(form, text="Profil", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
    profile_var = StringVar(value="Client")
    ctk.CTkOptionMenu(
        form,
        values=["Client", "Admin"],
        variable=profile_var,
        height=40,
        fg_color=COLORS["primary"],
        button_color=COLORS["primary"],
        button_hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 13),
    ).pack(fill="x", pady=(6, 12))

    ctk.CTkLabel(form, text="Mot de passe", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
    entryPasswordInscription = ctk.CTkEntry(
        form,
        height=40,
        show="*",
        fg_color=COLORS["field_bg"],
        border_color=COLORS["border"],
        placeholder_text="Min. 12, 2 majuscules, 1 chiffre, 1 caractère spécial",
    )
    entryPasswordInscription.pack(fill="x", pady=(6, 10))

    show_password_var = BooleanVar(value=False)

    def toggle_password_visibility():
        entryPasswordInscription.configure(show="" if show_password_var.get() else "*")

    ctk.CTkCheckBox(
        form,
        text="Afficher le mot de passe",
        text_color=COLORS["muted"],
        variable=show_password_var,
        command=toggle_password_visibility,
    ).pack(anchor="w")
    

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(16, 0))

    def on_submit_signup():
        username = entryUserNameInscription.get().strip()
        password = entryPasswordInscription.get().strip()
        profile = profile_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Attention", "Un des champs est vide.")
            return

        is_valid, error_message = validate_password_policy(
            password,
            min_uppercase=2,
            min_digits=1,
            min_special=1,
        )
        if not is_valid:
            messagebox.showwarning("Mot de passe invalide", error_message)
            return

        submit_inscription(entryUserNameInscription, entryPasswordInscription, profile_var)
        if callable(on_signup_success):
            schedule_navigation(on_signup_success, username=username, password=password, profile=profile)

    ctk.CTkButton(
        actions,
        text="Créer le compte",
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
        # Insertion de lambda, sinon Python exécute directement la fonction au lieu de l'associer au bouton.
        command=on_submit_signup,
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

    ctk.CTkButton(
        actions,
        text=back_button_text,
        height=42,
        fg_color=COLORS["surface"],
        hover_color="#e8ebf0",
        text_color=COLORS["text"],
        border_width=1,
        border_color=COLORS["border"],
        font=("Segoe UI", 14, "bold"),
        command=(lambda: schedule_navigation(on_back) if callable(on_back) else app.quit()),
    ).pack(side="left", fill="x", padx=(8, 8))

    ctk.CTkButton(
        actions,
        text="Annuler",
        height=42,
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        font=("Segoe UI", 14, "bold"),
        command=app.quit,
    ).pack(side="left", fill="x", padx=(8, 0))

    app.mainloop()
    cleanup_window(app)
    if callable(next_action):
        next_action()


if __name__ == "__main__":
    create_inscription_ui()