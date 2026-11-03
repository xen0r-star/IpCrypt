from tkinter import messagebox
import customtkinter as ctk

from pathlib import Path
from utils.auth_service import (
    NB_ADMINS_REQUIS_RESET,
    VALIDITE_VOTE_HEURES,
    a_deja_vote_reinitialisation,
    annuler_vote_reinitialisation,
    etat_reinitialisation_globale,
    voter_reinitialisation_globale,
)
ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ══════════════════════════════════════════════
# Interface CustomTkinter
# ══════════════════════════════════════════════

COLORS = {
    "bg": "#eef1f6",
    "surface": "#ffffff",
    "panel": "#f6f8fc",
    "primary": "#3f5fa8",
    "primary_hover": "#355190",
    "danger": "#b05f5f",
    "danger_hover": "#994f4f",
    "text": "#16233b",
    "muted": "#5a6b86",
    "border": "#cfd8e6",
    "success": "#3f7a52",
    "warning": "#a8741f",
}

MESSAGES = {
    "refuse": ("Action réservée aux administrateurs.", "danger"),
    "deja_vote": ("Tu as déjà voté. Il faut un autre administrateur pour valider.", "warning"),
    "en_attente": ("Vote enregistré. Un autre administrateur doit à son tour confirmer.", "warning"),
    "declenche": ("Réinitialisation validée : chaque utilisateur devra choisir un nouveau mot de passe à sa prochaine connexion.", "success"),
    "erreur": ("Opération impossible (voir la console).", "danger"),
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


def create_securite_admin_ui(on_back=None, user_id=None):
    """Fenêtre Sécurité (admins) : réinitialisation globale des mots de passe après vol de la base, validée par 2 administrateurs."""
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("Sécurité")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(True, True)
    app.minsize(720, 560)
    center_window(app, 720, 560)

    def schedule_navigation(callback, *args, **kwargs):
        """Stocke le callback et quitte mainloop; le callback s'exécute après cleanup_window."""
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=28, pady=20)

    ctk.CTkLabel(container, text="Sécurité", font=("Segoe UI", 34, "bold"), text_color=COLORS["text"]).pack(anchor="center")
    ctk.CTkLabel(
        container,
        text="Réinitialisation globale des mots de passe",
        font=("Segoe UI", 15),
        text_color=COLORS["muted"],
    ).pack(anchor="center", pady=(4, 16))

    card = ctk.CTkFrame(container, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"], corner_radius=14)
    card.pack(fill="both", expand=True)

    ctk.CTkLabel(
        card,
        text=(
            "À utiliser si l'on apprend que la base de données a été volée.\n"
            f"{NB_ADMINS_REQUIS_RESET} administrateurs différents doivent confirmer (dans un délai de {VALIDITE_VOTE_HEURES} h).\n\n"
            "Une fois validé, TOUS les utilisateurs (admins compris) devront choisir un nouveau mot de passe, différent de l'ancien, à leur prochaine connexion. Aucun compte n'est bloqué et les sessions ouvertes ne sont pas coupées."
        ),
        font=("Segoe UI", 13),
        text_color=COLORS["text"],
        justify="left",
        wraplength=620,
    ).pack(anchor="w", padx=22, pady=(20, 12))

    statut_frame = ctk.CTkFrame(card, fg_color=COLORS["panel"], border_width=1, border_color=COLORS["border"], corner_radius=12)
    statut_frame.pack(fill="x", padx=22, pady=(0, 12))
    label_votes = ctk.CTkLabel(statut_frame, text="", font=("Segoe UI", 14, "bold"), text_color=COLORS["primary"], justify="left")
    label_votes.pack(anchor="w", padx=16, pady=(12, 2))
    label_mon_vote = ctk.CTkLabel(statut_frame, text="", font=("Segoe UI", 12), text_color=COLORS["muted"])
    label_mon_vote.pack(anchor="w", padx=16, pady=(0, 12))

    label_message = ctk.CTkLabel(card, text="", font=("Segoe UI", 13, "bold"), text_color=COLORS["muted"], justify="left", wraplength=620)
    label_message.pack(anchor="w", padx=22, pady=(0, 16))

    def rafraichir_statut():
        """Affiche les votes encore valables (qui a déjà voté) et si l'utilisateur connecté a voté."""
        votants = etat_reinitialisation_globale()
        if votants is None:
            label_votes.configure(text="Statut indisponible (voir la console)", text_color=COLORS["danger"])
            label_mon_vote.configure(text="")
            return
        liste = ", ".join(votants) if votants else "aucun"
        label_votes.configure(text=f"Validations : {len(votants)} / {NB_ADMINS_REQUIS_RESET}   ({liste})", text_color=COLORS["primary"])
        label_mon_vote.configure(text="Tu as déjà voté." if a_deja_vote_reinitialisation(user_id) else "Tu n'as pas encore voté.")

    def afficher(statut):
        texte, couleur = MESSAGES.get(statut, MESSAGES["erreur"])
        label_message.configure(text=texte, text_color=COLORS[couleur])

    def on_forcer():
        """Demande confirmation puis enregistre le vote de l'admin ; le déclenchement est décidé par la base (2 admins distincts)."""
        if not messagebox.askyesno(
            "Confirmation",
            "Voter pour forcer le changement de mot de passe de TOUS les utilisateurs ?\n\n"
            "La réinitialisation ne démarre que si un deuxième administrateur confirme aussi.",
            icon="warning",
        ):
            return
        resultat = voter_reinitialisation_globale(user_id)
        afficher(resultat["statut"])
        rafraichir_statut()

    def on_annuler():
        """Retire le vote de l'utilisateur connecté."""
        if annuler_vote_reinitialisation(user_id):
            label_message.configure(text="Ton vote a été retiré.", text_color=COLORS["muted"])
        else:
            label_message.configure(text="Tu n'avais pas de vote en cours.", text_color=COLORS["muted"])
        rafraichir_statut()

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(14, 0))

    ctk.CTkButton(
        actions,
        text="Forcer le changement de tous les mots de passe",
        height=42,
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        font=("Segoe UI", 14, "bold"),
        command=on_forcer,
    ).pack(side="left", expand=True, fill="x", padx=(0, 8))

    ctk.CTkButton(
        actions,
        text="Annuler mon vote",
        height=42,
        fg_color=COLORS["surface"],
        hover_color="#e8ebf0",
        text_color=COLORS["text"],
        border_width=1,
        border_color=COLORS["border"],
        font=("Segoe UI", 14, "bold"),
        command=on_annuler,
    ).pack(side="left", fill="x", padx=(8, 0))

    ctk.CTkButton(
        actions,
        text="Retour au menu",
        height=42,
        fg_color=COLORS["surface"],
        hover_color="#e8ebf0",
        text_color=COLORS["text"],
        border_width=1,
        border_color=COLORS["border"],
        font=("Segoe UI", 14, "bold"),
        command=(lambda: schedule_navigation(on_back) if callable(on_back) else app.quit()),
    ).pack(side="left", fill="x", padx=(8, 0))

    rafraichir_statut()

    app.mainloop()
    cleanup_window(app)
    if callable(next_action):
        next_action()


if __name__ == "__main__":
    create_securite_admin_ui()
