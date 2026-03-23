from tkinter import messagebox
import customtkinter as ctk

try:
    from utils.password_policy import validate_password_policy
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from utils.password_policy import validate_password_policy

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#f4f6fb",
    "surface": "#ffffff",
    "primary": "#2f6fed",
    "primary_hover": "#2459c9",
    "danger": "#d94848",
    "danger_hover": "#b93a3a",
    "text": "#17233a",
    "muted": "#5b6b84",
    "border": "#d7deea",
    "field_bg": "#f9fbff",
}

SPACING = {
    "outer_x": 28,
    "outer_y": 20,
    "inner": 14,
}


def center_window(window: ctk.CTk, width: int, height: int) -> None:
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    pos_x = int((screen_w - width) / 2)
    pos_y = int((screen_h - height) / 2)
    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


def cleanup_window(window: ctk.CTk) -> None:
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


def create_connexion_ui(on_login_success=None, on_go_to_signup=None):
    app = ctk.CTk()
    next_action = None
    app.title("Connexion")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(False, False)
    center_window(app, 560, 430)

    def schedule_navigation(callback, *args, **kwargs):
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=SPACING["outer_x"], pady=SPACING["outer_y"])

    ctk.CTkLabel(
        container,
        text="Connexion",
        font=("Segoe UI", 34, "bold"),
        text_color=COLORS["text"],
    ).pack(anchor="center")

    ctk.CTkLabel(
        container,
        text="Accede a ton espace reseau",
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
    card.pack(fill="x", padx=2, pady=(0, 16))

    form = ctk.CTkFrame(card, fg_color="transparent")
    form.pack(fill="x", padx=20, pady=18)

    ctk.CTkLabel(form, text="Nom utilisateur", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
    entryUserName = ctk.CTkEntry(
        form,
        height=40,
        fg_color=COLORS["field_bg"],
        border_color=COLORS["border"],
        placeholder_text="Ex: jean_dupont (min. 3 caracteres)",
    )
    entryUserName.pack(fill="x", pady=(6, 12))

    ctk.CTkLabel(form, text="Mot de passe", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
    entryPassword = ctk.CTkEntry(
        form,
        height=40,
        show="*",
        fg_color=COLORS["field_bg"],
        border_color=COLORS["border"],
        placeholder_text="Min 12, 2 majuscules, 1 chiffre, 1 special",
    )
    entryPassword.pack(fill="x", pady=(6, 10))

    def toggle_password():
        entryPassword.configure(show="" if entryPassword.cget("show") == "*" else "*")

    ctk.CTkCheckBox(form, text="Afficher le mot de passe", text_color=COLORS["muted"], command=toggle_password).pack(anchor="w")

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x")

    def on_submit():
        valeurUserName = entryUserName.get().strip()
        valeurPassword = entryPassword.get().strip()

        if not valeurUserName or not valeurPassword:
            messagebox.showwarning("Attention", "Un des champs est vide.")
            return

        is_valid, error_message = validate_password_policy(
            valeurPassword,
            min_uppercase=2,
            min_digits=1,
            min_special=1,
        )
        if not is_valid:
            messagebox.showwarning("Mot de passe invalide", error_message)
            return

        else:
            is_admin = "admin" in valeurUserName.lower()
            if callable(on_login_success):
                schedule_navigation(on_login_success, is_admin=is_admin, username=valeurUserName)
            else:
                messagebox.showinfo("UserName", f"Nom d'utilisateur : {valeurUserName}\nMot de passe : {valeurPassword}")

    ctk.CTkButton(
        actions,
        text="Se connecter",
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
        command=on_submit,
    ).pack(side="left", expand=True, fill="x", padx=(0, 8))

    if callable(on_go_to_signup):
        ctk.CTkButton(
            actions,
            text="Inscription",
            height=42,
            fg_color=COLORS["surface"],
            hover_color="#eef2fb",
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            font=("Segoe UI", 14, "bold"),
            command=lambda: schedule_navigation(on_go_to_signup),
        ).pack(side="left", fill="x", padx=(8, 8))

    ctk.CTkButton(
        actions,
        text="Quitter",
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
    create_connexion_ui()