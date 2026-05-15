import customtkinter as ctk

from pathlib import Path
ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

# ══════════════════════════════════════════════
# Logique métier
# ══════════════════════════════════════════════

def definirClasse(premOctet):
    """Retourne la classe (A–E) d'une adresse IP à partir de son premier octet."""
    octet = int(premOctet)
    match octet:
        case _ if 1 <= octet <= 126:
            return "A"
        case _ if 128 <= octet <= 191:
            return "B"
        case _ if 192 <= octet <= 223:
            return "C"
        case _ if 224 <= octet <= 240:
            return "D"
        case _:
            return "E"


def defAdresseReseau(segment, classe):
    """Retourne l'adresse réseau classful en mettant à zéro les octets hôte selon la classe."""
    match classe:
        case "A":
            return f"{int(segment[0])}.0.0.0"
        case "B":
            return f"{int(segment[0])}.{int(segment[1])}.0.0"
        case "C":
            return f"{int(segment[0])}.{int(segment[1])}.{int(segment[2])}.0"
        case _:
            return "N/A"


def valider_masque(masque_segments):
    """Vérifie si le masque est structurellement valide (suite continue de 1 puis de 0)."""
    try:
        # Convertit les 4 octets en une seule chaîne binaire de 32 caractères
        bits = "".join(bin(int(octet))[2:].zfill(8) for octet in masque_segments)
        
        # Un masque valide ne doit JAMAIS avoir de '1' après un '0' (donc pas de séquence "01")
        # Et il doit obligatoirement commencer par un '1' (le premier bit ne peut pas être 0)
        return "01" not in bits and bits.startswith("1")
    except ValueError:
        return False


def defAdresseSousReseau(segment, masque):
    """Calcule l'adresse de sous-réseau par ET logique bit à bit entre l'IP et le masque."""
    res = []
    for i in range(4):
        octet_ip = int(segment[i])
        octet_masque = int(masque[i])
        res.append(str(octet_ip & octet_masque))
    return ".".join(res)


# ══════════════════════════════════════════════
# Interface CustomTkinter
# ══════════════════════════════════════════════

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

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


# Listes globales réinitialisées à chaque ouverture de fenêtre.
group_entries = []
result_labels = {}


def ip_octet_group(parent: ctk.CTkFrame, label_text: str) -> None:
    """Crée une ligne de 4 champs de saisie pour une adresse IPv4 (validation : chiffres uniquement, max 3 par octet)."""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(row, text=label_text, width=90, anchor="w", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(side="left")

    octet_box = ctk.CTkFrame(
        row,
        fg_color=COLORS["panel"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=10,
    )
    octet_box.pack(side="left", fill="x", expand=True)

    inner = ctk.CTkFrame(octet_box, fg_color="transparent")
    inner.pack(padx=12, pady=10)

    vcmd = (parent.winfo_toplevel().register(lambda val: val.isdecimal() and len(val) <= 3 or val == ""), "%P")

    for i in range(4):
        entry = ctk.CTkEntry(inner, width=55, height=36, justify="center", fg_color=COLORS["surface"], border_color=COLORS["border"], validate="key", validatecommand=vcmd)
        entry.pack(side="left")
        group_entries.append(entry)
        if i < 3:
            ctk.CTkLabel(inner, text=".", font=("Segoe UI", 18, "bold"), text_color=COLORS["muted"]).pack(side="left", padx=6)


def lire_octets(group: list) -> list | None:
    """Extrait les 4 octets d'un groupe de champs Entry. Retourne None si un octet est vide ou hors de 0–255."""
    octets = []
    for entry in group:
        val = entry.get().strip()
        if not val.isdecimal() or not (0 <= int(val) <= 255):
            return None
        octets.append(str(int(val)))  # Nettoyé : suppression du .zfill(3) problématique
    return octets


def create_get_network_ui(on_back=None):
    """Fenêtre Définir réseau et sous-réseau : calcule l'adresse réseau classful et l'adresse de sous-réseau par masque personnalisé."""
    group_entries.clear()
    result_labels.clear()
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("Définir réseau et sous-réseau")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(True, True)
    app.minsize(720, 520)
    center_window(app, 720, 520)

    def schedule_navigation(callback, *args, **kwargs):
        """Stocke le callback et quitte mainloop ; le callback s'exécute après cleanup_window."""
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="x", padx=28, pady=20)

    ctk.CTkLabel(
        container,
        text="Définir réseau et sous-réseau",
        font=("Segoe UI", 34, "bold"),
        text_color=COLORS["text"],
    ).pack(anchor="center")

    ctk.CTkLabel(
        container,
        text="Saisis une IP valide pour afficher les détails",
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

    inputs_section = ctk.CTkFrame(card, fg_color="transparent")
    inputs_section.pack(fill="x", padx=20, pady=(18, 10))

    ip_octet_group(inputs_section, "IP")
    ip_octet_group(inputs_section, "Masque")

    results = ctk.CTkFrame(
        card,
        fg_color=COLORS["panel"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=12,
    )
    results.pack(fill="x", padx=20, pady=(0, 20))

    for label_text in ["Adresse réseau", "Adresse sous-réseau"]:
        row = ctk.CTkFrame(results, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=5)
        ctk.CTkLabel(row, text=label_text + " :", width=180, anchor="e",
                     font=("Segoe UI", 13), text_color=COLORS["text"]).pack(side="left")
        val_label = ctk.CTkLabel(row, text="-", anchor="w",
                                 font=("Segoe UI", 13, "bold"), text_color=COLORS["muted"])
        val_label.pack(side="left", padx=10)
        result_labels[label_text] = val_label

    def on_verify():
        """Lit IP et masque, applique les validations strictes puis calcule les adresses."""
        # Réinitialisation visuelle par défaut avant calcul
        result_labels["Adresse réseau"].configure(text="-", text_color=COLORS["muted"])
        result_labels["Adresse sous-réseau"].configure(text="-", text_color=COLORS["muted"])

        octetsIP     = lire_octets(group_entries[:4])
        octetsMasque = lire_octets(group_entries[4:])

        # 1. Vérification des caractères et de la plage numérique (0-255)
        if not octetsIP:
            result_labels["Adresse réseau"].configure(text="IP Invalide (0-255 ou texte détecté)", text_color=COLORS["danger"])
            return

        if not octetsMasque:
            result_labels["Adresse sous-réseau"].configure(text="Masque Invalide (0-255 ou texte détecté)", text_color=COLORS["danger"])
            return

        # 2. Validation de la structure binaire continue du masque de sous-réseau
        if not valider_masque(octetsMasque):
            result_labels["Adresse sous-réseau"].configure(text="Masque structurellement invalide", text_color=COLORS["danger"])
            return

        # 3. Traitement et mise à jour de l'affichage si tout est correct
        classe = definirClasse(octetsIP[0])
        adresseReseau = defAdresseReseau(octetsIP, classe)
        adresseSousReseau = defAdresseSousReseau(octetsIP, octetsMasque)
        
        result_labels["Adresse réseau"].configure(text=adresseReseau, text_color=COLORS["primary"])
        result_labels["Adresse sous-réseau"].configure(text=adresseSousReseau, text_color=COLORS["primary"])

    def on_clear():
        """Efface les champs de saisie et réinitialise les labels de résultats."""
        def clear_recursive(container):
            for widget in container.winfo_children():
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                    clear_recursive(widget)
        clear_recursive(inputs_section)
        for label in result_labels.values():
            label.configure(text="-", text_color=COLORS["muted"])

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(14, 0))

    ctk.CTkButton(
        actions,
        text="Vérifier",
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
        command=on_verify,
    ).pack(side="left", expand=True, fill="x", padx=(0, 8))

    ctk.CTkButton(
        actions,
        text="Effacer",
        height=42,
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        font=("Segoe UI", 14, "bold"),
        command=on_clear,
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

    app.mainloop()
    cleanup_window(app)
    if callable(next_action):
        next_action()


if __name__ == "__main__":
    create_get_network_ui()