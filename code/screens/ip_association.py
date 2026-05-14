import customtkinter as ctk

from pathlib import Path
ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ══════════════════════════════════════════════
# Logique métier
# ══════════════════════════════════════════════

def calcule_adresse_reseau(ip1, masque1, ip2, masque2) -> tuple[list, list, str, bool]:
    """
    Calcule les adresses réseau par ET bit à bit et détermine la visibilité bilatérale.
    Retourne (reseau1, reseau2, verdict, meme_reseau).
    """
    reseau1 = [int(ip1[i]) & int(masque1[i]) for i in range(4)]
    reseau2 = [int(ip2[i]) & int(masque2[i]) for i in range(4)]

    # Calcul croisé : est-ce que chaque hôte voit l'autre dans son propre réseau ?
    ip2_vu_par_masque1 = [int(ip2[i]) & int(masque1[i]) for i in range(4)]
    ip1_vu_par_masque2 = [int(ip1[i]) & int(masque2[i]) for i in range(4)]

    a_voit_b = ip2_vu_par_masque1 == reseau1
    b_voit_a = ip1_vu_par_masque2 == reseau2

    if a_voit_b and b_voit_a:
        verdict = "A et B sont dans le même réseau."
    elif a_voit_b:
        verdict = "A voit B mais B ne voit pas A."
    elif b_voit_a:
        verdict = "B voit A mais A ne voit pas B."
    else:
        verdict = "A et B ne se voient pas."

    return reseau1, reseau2, verdict, (a_voit_b and b_voit_a)


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
    "error": "#b05f5f",
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


def ip_octet_group(parent: ctk.CTkFrame, label_text: str, entries_store: list) -> None:
    """Crée une ligne de 4 champs de saisie pour une adresse IPv4 et ajoute le groupe dans entries_store."""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=(0, 12))

    ctk.CTkLabel(row, text=label_text, width=110, anchor="w", font=("Segoe UI", 14, "bold"), text_color=COLORS["text"]).pack(side="left")

    octet_box = ctk.CTkFrame(row, fg_color=COLORS["panel"], border_width=1, border_color=COLORS["border"], corner_radius=10)
    octet_box.pack(side="left", fill="x", expand=True)

    inner = ctk.CTkFrame(octet_box, fg_color="transparent")
    inner.pack(padx=14, pady=12)

    vcmd = (parent.winfo_toplevel().register(lambda val: val.isdigit() and len(val) <= 3 or val == ""), "%P")

    group_entries = []
    for i in range(4):
        entry = ctk.CTkEntry(inner, width=62, height=40, justify="center", fg_color=COLORS["surface"], border_color=COLORS["border"], validate="key", validatecommand=vcmd)
        entry.pack(side="left")
        group_entries.append(entry)
        if i < 3:
            ctk.CTkLabel(inner, text=".", font=("Segoe UI", 20, "bold"), text_color=COLORS["muted"]).pack(side="left", padx=6)

    entries_store.append(group_entries)


def lire_octets(group: list) -> list | None:
    """Extrait les 4 octets d'un groupe de champs Entry. Retourne None si un octet est vide ou hors de 0–255."""
    octets = []
    for entry in group:
        val = entry.get().strip()
        if not val.isdigit() or not (0 <= int(val) <= 255):
            return None
        octets.append(str(int(val)).zfill(3))
    return octets


def create_ip_association_ui(on_back=None):
    """Fenêtre IP Association : compare deux adresses IP/masques et détermine leur visibilité réciproque."""
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("IP Association")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(True, True)
    center_window(app, 960, 680)

    def schedule_navigation(callback, *args, **kwargs):
        """Stocke le callback et quitte mainloop ; le callback s'exécute après cleanup_window."""
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    # entries_store[0] = IP1, [1] = Masque1, [2] = IP2, [3] = Masque2
    entries_store = []

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=34, pady=24)

    ctk.CTkLabel(container, text="IP Association", font=("Segoe UI", 38, "bold"), text_color=COLORS["text"]).pack(anchor="center")
    ctk.CTkLabel(container, text="Compare deux adresses IP et détermine si elles sont dans le même réseau", font=("Segoe UI", 16), text_color=COLORS["muted"]).pack(anchor="center", pady=(6, 20))

    card = ctk.CTkFrame(container, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"], corner_radius=14)
    card.pack(fill="both", expand=True)

    section_1 = ctk.CTkFrame(card, fg_color=COLORS["panel"], border_width=1, border_color=COLORS["border"], corner_radius=12)
    section_1.pack(fill="x", padx=24, pady=(20, 12))
    ctk.CTkLabel(section_1, text="Adresse 1", font=("Segoe UI", 15, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 10))
    ip_octet_group(section_1, "IP 1", entries_store)
    ip_octet_group(section_1, "Masque 1", entries_store)

    section_2 = ctk.CTkFrame(card, fg_color=COLORS["panel"], border_width=1, border_color=COLORS["border"], corner_radius=12)
    section_2.pack(fill="x", padx=24, pady=(0, 16))
    ctk.CTkLabel(section_2, text="Adresse 2", font=("Segoe UI", 15, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 10))
    ip_octet_group(section_2, "IP 2", entries_store)
    ip_octet_group(section_2, "Masque 2", entries_store)

    result_frame = ctk.CTkFrame(card, fg_color=COLORS["panel"], border_width=1, border_color=COLORS["border"], corner_radius=12)
    result_frame.pack(fill="x", padx=24, pady=(0, 16))

    result_label = ctk.CTkLabel(result_frame, text="", font=("Segoe UI", 14), text_color=COLORS["muted"], justify="left")
    result_label.pack(anchor="w", padx=16, pady=14)

    def on_inputs_changed(_event=None):
        """Avertit l'utilisateur que les valeurs ont changé et que le résultat affiché n'est plus à jour."""
        result_label.configure(
            text="Valeurs modifiées. Clique sur Associer pour recalculer.",
            text_color=COLORS["muted"],
        )

    for group in entries_store:
        for entry in group:
            entry.bind("<KeyRelease>", on_inputs_changed)
            entry.bind("<FocusOut>", on_inputs_changed)

    def on_associer():
        """Lit les quatre groupes d'octets, calcule les réseaux et affiche le verdict de visibilité."""
        ip1     = lire_octets(entries_store[0])
        masque1 = lire_octets(entries_store[1])
        ip2     = lire_octets(entries_store[2])
        masque2 = lire_octets(entries_store[3])

        if any(v is None for v in [ip1, masque1, ip2, masque2]):
            result_label.configure(text="Erreur : un ou plusieurs octets sont invalides (0-255).", text_color=COLORS["error"])
            return

        reseau1, reseau2, verdict, meme_reseau = calcule_adresse_reseau(ip1, masque1, ip2, masque2)

        r1_str = '.'.join(str(octet) for octet in reseau1)
        r2_str = '.'.join(str(octet) for octet in reseau2)

        couleur = COLORS["success"] if meme_reseau else COLORS["error"]

        result_label.configure(
            text=f"Réseau 1 : {r1_str}\nRéseau 2 : {r2_str}\n\n{verdict}",
            text_color=couleur
        )

    def on_effacer():
        """Vide tous les champs de saisie et réinitialise le label de résultat."""
        for group in entries_store:
            for entry in group:
                entry.delete(0, "end")
        result_label.configure(text="", text_color=COLORS["muted"])

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(16, 0))

    ctk.CTkButton(actions, text="Associer", height=46, fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"], font=("Segoe UI", 15, "bold"), command=on_associer).pack(side="left", expand=True, fill="x", padx=(0, 6))
    ctk.CTkButton(actions, text="Effacer", height=46, fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"], font=("Segoe UI", 15, "bold"), command=on_effacer).pack(side="left", expand=True, fill="x", padx=(6, 6))
    ctk.CTkButton(
        actions,
        text="Retour au menu",
        height=46,
        fg_color=COLORS["surface"],
        hover_color="#e8ebf0",
        text_color=COLORS["text"],
        border_width=1,
        border_color=COLORS["border"],
        font=("Segoe UI", 15, "bold"),
        command=(lambda: schedule_navigation(on_back) if callable(on_back) else app.quit()),
    ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    app.mainloop()
    cleanup_window(app)
    if callable(next_action):
        next_action()


if __name__ == "__main__":
    create_ip_association_ui()
