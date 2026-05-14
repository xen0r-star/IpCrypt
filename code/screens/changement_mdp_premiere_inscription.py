from tkinter import BooleanVar, messagebox

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

# ══════════════════════════════════════════════
# Interface CustomTkinter
# ══════════════════════════════════════════════

COLORS = {
    "bg": "#eef1f6",
    "surface": "#ffffff",
    "primary": "#3f5fa8",
    "primary_hover": "#355190",
    "danger": "#b05f5f",
    "danger_hover": "#994f4f",
    "text": "#16233b",
    "muted": "#5a6b86",
    "border": "#cfd8e6",
    "field_bg": "#f6f8fc",
}


def center_window(window: ctk.CTk, width: int, height: int) -> None:
    """Centre la fenêtre sur l'écran."""
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    pos_x = int((screen_w - width) / 2)
    pos_y = int((screen_h - height) / 2)
    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


def cleanup_window(window: ctk.CTk) -> None:
    """Détruit la fenêtre proprement en annulant les callbacks after() pour éviter les TclError sur widgets morts."""
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
        pass


def create_first_connection_ui(username, on_password_changed=None, on_back=None, back_button_text="Annuler"):
    """Fenêtre de première connexion : force l'utilisateur à choisir un nouveau mot de passe avant d'accéder au menu."""
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("Changement mot de passe lors de la premiere inscription")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(True, True)
    app.minsize(600, 520)
    center_window(app, 600, 520)

    def schedule_navigation(callback, *args, **kwargs):
        """Stocke le callback et quitte mainloop ; le callback s'exécute après cleanup_window."""
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=28, pady=20)

    ctk.CTkLabel(
        container,
        text="Premiere connexion",
        font=("Segoe UI", 34, "bold"),
        text_color=COLORS["text"],
    ).pack(anchor="center")

    ctk.CTkLabel(
        container,
        text="Choisis un nouveau mot de passe pour ton compte",
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

    ctk.CTkLabel(form, text="Compte concerne", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
    ctk.CTkLabel(
        form,
        text=username,
        font=("Segoe UI", 15, "bold"),
        text_color=COLORS["primary"],
    ).pack(anchor="w", pady=(6, 12))

    ctk.CTkLabel(form, text="Nouveau mot de passe", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
    entry_new_password = ctk.CTkEntry(
        form,
        height=40,
        show="*",
        fg_color=COLORS["field_bg"],
        border_color=COLORS["border"],
        placeholder_text="Min. 12, 1 minuscule, 2 majuscules, 1 chiffre, 1 caractère spécial",
    )
    entry_new_password.pack(fill="x", pady=(6, 12))

    ctk.CTkLabel(form, text="Confirmer le nouveau mot de passe", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
    entry_confirm_password = ctk.CTkEntry(
        form,
        height=40,
        show="*",
        fg_color=COLORS["field_bg"],
        border_color=COLORS["border"],
        placeholder_text="Retape exactement le nouveau mot de passe",
    )
    entry_confirm_password.pack(fill="x", pady=(6, 10))

    show_password_var = BooleanVar(value=False)

    def toggle_password_visibility():
        # Seul le premier champ se démasque : l'utilisateur voit ce qu'il tape,
        # puis doit ressaisir de mémoire dans le champ de confirmation (toujours masqué).
        show_char = "" if show_password_var.get() else "*"
        entry_new_password.configure(show=show_char)

    ctk.CTkCheckBox(
        form,
        text="Afficher le mot de passe",
        text_color=COLORS["muted"],
        variable=show_password_var,
        command=toggle_password_visibility,
    ).pack(anchor="w")

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(16, 0))

    def on_submit_password_change():
        """Vérifie la correspondance des deux champs, valide la policy puis transmet au callback."""
        new_password = entry_new_password.get().strip()
        confirm_password = entry_confirm_password.get().strip()

        if not new_password or not confirm_password:
            messagebox.showwarning("Attention", "Un des champs est vide.")
            return

        if new_password != confirm_password:
            messagebox.showwarning("Mot de passe invalide", "Les deux mots de passe saisis sont differents.")
            return

        is_valid, error_message = validate_password_policy(
            new_password,
            min_lowercase=1,
            min_uppercase=2,
            min_digits=1,
            min_special=1,
        )
        if not is_valid:
            messagebox.showwarning("Mot de passe invalide", error_message)
            return

        if callable(on_password_changed):
            schedule_navigation(on_password_changed, username=username, new_password=new_password)

    ctk.CTkButton(
        actions,
        text="Changer le mot de passe",
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
        command=on_submit_password_change,
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

    app.mainloop()
    cleanup_window(app)
    if callable(next_action):
        next_action()


# Alias mort — main.py importe create_inscription_ui depuis register_screen.
def create_inscription_ui(on_signup_success=None, on_back=None, back_button_text="Connexion"):
    create_first_connection_ui(
        username="",
        on_password_changed=on_signup_success,
        on_back=on_back,
        back_button_text=back_button_text,
    )


if __name__ == "__main__":
    create_first_connection_ui(username="utilisateur_test")
