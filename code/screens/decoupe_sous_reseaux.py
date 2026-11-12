from tkinter import messagebox, ttk
import customtkinter as ctk

from pathlib import Path
from utils.data_service import enregistrer_decoupe_sous_reseaux, lister_decoupes_sous_reseaux
from screens.historique_widget import creer_panneau_historique, remplir_octets
ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

# ══════════════════════════════════════════════
# Logique métier
# ══════════════════════════════════════════════

BITS_HOTE_MIN = 2
LIMITE_LIGNES = 500
CIDR_PAR_CLASSE = {"A": 8, "B": 16, "C": 24}


def classe_depuis_octet(premier_octet: int) -> str:
    """Retourne la classe (A–E) d'une adresse IP à partir de son premier octet."""
    if premier_octet <= 127:
        return "A"
    if premier_octet <= 191:
        return "B"
    if premier_octet <= 223:
        return "C"
    if premier_octet <= 239:
        return "D"
    return "E"


def octets_vers_entier(octets) -> int:
    """Convertit 4 octets en un seul grand nombre (entier 32 bits).

    Exemple : 192.168.1.10 -> 192*256^3 + 168*256^2 + 1*256 + 10
    """
    valeur = 0
    for octet in octets:
        valeur = valeur * 256 + int(octet)
    return valeur


def entier_vers_texte(valeur: int) -> str:
    """Convertit un entier 32 bits en adresse texte 'a.b.c.d'."""
    octet1 = (valeur // 256**3) % 256
    octet2 = (valeur // 256**2) % 256
    octet3 = (valeur // 256) % 256
    octet4 = valeur % 256
    return f"{octet1}.{octet2}.{octet3}.{octet4}"


def masque_depuis_cidr(cidr: int) -> int:
    """Retourne le masque (sous forme d'entier) correspondant à un préfixe CIDR.

    Exemple : /24 -> 255.255.255.0
    """
    nb_bits_hote = 32 - cidr
    return 2**32 - 2**nb_bits_hote


def bits_a_emprunter(nb_sous_reseaux: int) -> int:
    """Nombre de bits à emprunter pour avoir au moins nb_sous_reseaux sous-réseaux."""
    bits = 0
    while 2**bits < nb_sous_reseaux:
        bits += 1
    return bits


def nb_sous_reseaux_max(cidr_base: int) -> int:
    """Nombre max de sous-réseaux pour un préfixe de base,
    en gardant au moins BITS_HOTE_MIN bits d'hôte."""
    return 2 ** (32 - BITS_HOTE_MIN - cidr_base)


def calculer_decoupe(octets_ip, nb_demande: int) -> dict:
    """
    Découpe le réseau classful de l'IP donnée en au moins nb_demande
    sous-réseaux de même taille.

    Lève ValueError si la découpe est impossible.

    On emprunte n bits tels que 2**n >= nb_demande :
    on obtient donc 2**n sous-réseaux (>= nb_demande).
    """
    premier_octet = int(octets_ip[0])
    classe = classe_depuis_octet(premier_octet)

    # Vérifications : on refuse les cas impossibles
    if classe in ("D", "E"):
        raise ValueError(
            f"Classe {classe} : pas de découpe possible "
            f"(seules les classes A, B et C se découpent)."
        )
    if premier_octet in (0, 127):
        raise ValueError(
            "Réseau réservé (0.0.0.0/8 ou 127.0.0.0/8) : pas de découpe possible."
        )
    if nb_demande < 2:
        raise ValueError("Il faut demander au moins 2 sous-réseaux.")

    cidr_base = CIDR_PAR_CLASSE[classe]
    maximum = nb_sous_reseaux_max(cidr_base)
    if nb_demande > maximum:
        raise ValueError(
            f"Classe {classe} : {maximum} sous-réseaux au maximum "
            f"(il faut garder 2 hôtes utilisables par sous-réseau)."
        )

    # Calculs principaux
    bits = bits_a_emprunter(nb_demande)
    nouveau_cidr = cidr_base + bits
    taille_bloc = 2 ** (32 - nouveau_cidr)

    # Adresse du réseau de base : on remet à zéro la partie "hôte" de l'IP
    ip_entier = octets_vers_entier(octets_ip)
    taille_reseau_base = 2 ** (32 - cidr_base)
    base = ip_entier - (ip_entier % taille_reseau_base)

    return {
        "classe": classe,
        "adresse_reseau": entier_vers_texte(base),
        "cidr_base": cidr_base,
        "masque_base": entier_vers_texte(masque_depuis_cidr(cidr_base)),
        "bits_empruntes": bits,
        "nb_demande": nb_demande,
        "nb_obtenus": 2**bits,
        "nouveau_cidr": nouveau_cidr,
        "nouveau_masque": entier_vers_texte(masque_depuis_cidr(nouveau_cidr)),
        "taille_bloc": taille_bloc,
        "hotes_par_sous_reseau": taille_bloc - 2,
        "_base": base,
    }


def sous_reseau(decoupe: dict, numero: int) -> dict:
    """Détail du sous-réseau n° 'numero' (0 = premier)
    d'une découpe calculée par calculer_decoupe."""
    debut = decoupe["_base"] + numero * decoupe["taille_bloc"]
    broadcast = debut + decoupe["taille_bloc"] - 1
    return {
        "numero": numero + 1,
        "reseau": entier_vers_texte(debut),
        "premier_hote": entier_vers_texte(debut + 1),
        "dernier_hote": entier_vers_texte(broadcast - 1),
        "broadcast": entier_vers_texte(broadcast),
    }


def lister_sous_reseaux(decoupe: dict, limite: int = LIMITE_LIGNES) -> list:
    """Détail des 'limite' premiers sous-réseaux
    (une classe A découpée à fond en compte plusieurs millions)."""
    nombre_a_afficher = min(decoupe["nb_obtenus"], limite)
    liste = []
    for i in range(nombre_a_afficher):
        liste.append(sous_reseau(decoupe, i))
    return liste


# ══════════════════════════════════════════════
# Interface CustomTkinter
# (le calcul de la découpe est dans utils/calcul_sous_reseaux.py)
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


def ip_octet_group(parent: ctk.CTkFrame, label_text: str) -> list:
    """Crée une ligne de 4 champs de saisie pour une adresse IPv4 (chiffres uniquement, max 3 par octet) et retourne les 4 champs."""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(row, text=label_text, width=150, anchor="w", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(side="left")

    octet_box = ctk.CTkFrame(row, fg_color=COLORS["panel"], border_width=1, border_color=COLORS["border"], corner_radius=10)
    octet_box.pack(side="left", fill="x", expand=True)

    inner = ctk.CTkFrame(octet_box, fg_color="transparent")
    inner.pack(padx=12, pady=10)

    vcmd = (parent.winfo_toplevel().register(lambda val: val.isdecimal() and len(val) <= 3 or val == ""), "%P")

    entries = []
    for i in range(4):
        entry = ctk.CTkEntry(inner, width=55, height=36, justify="center", fg_color=COLORS["surface"], border_color=COLORS["border"], validate="key", validatecommand=vcmd)
        entry.pack(side="left")
        entries.append(entry)
        if i < 3:
            ctk.CTkLabel(inner, text=".", font=("Segoe UI", 18, "bold"), text_color=COLORS["muted"]).pack(side="left", padx=6)
    return entries


def lire_octets(entries: list) -> list | None:
    """Extrait les 4 octets (entiers) d'un groupe de champs. Retourne None si un octet est vide ou hors de 0–255."""
    octets = []
    for entry in entries:
        val = entry.get().strip()
        if not val.isdecimal() or not (0 <= int(val) <= 255):
            return None
        octets.append(int(val))
    return octets


def create_decoupe_ui(on_back=None, user_id=None):
    """Fenêtre Découpe en sous-réseaux : découpe le réseau classful d'une IP en N sous-réseaux et mémorise la découpe."""
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("Découpe en sous-réseaux")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(True, True)
    app.minsize(960, 700)
    center_window(app, 960, 760)

    def schedule_navigation(callback, *args, **kwargs):
        """Stocke le callback et quitte mainloop ; le callback s'exécute après cleanup_window."""
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=34, pady=24)

    ctk.CTkLabel(container, text="Découpe en sous-réseaux", font=("Segoe UI", 34, "bold"), text_color=COLORS["text"]).pack(anchor="center")
    ctk.CTkLabel(
        container,
        text="Découpe le réseau (classful) d'une IP selon le nombre de sous-réseaux souhaités",
        font=("Segoe UI", 15),
        text_color=COLORS["muted"],
    ).pack(anchor="center", pady=(4, 16))

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(16, 0), side="bottom")

    card = ctk.CTkScrollableFrame(container, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"], corner_radius=14)
    card.pack(fill="both", expand=True)

    # -- Saisie ----------------------------------------------------------
    inputs_section = ctk.CTkFrame(card, fg_color="transparent")
    inputs_section.pack(fill="x", padx=20, pady=(18, 6))

    entries_ip = ip_octet_group(inputs_section, "IP du réseau")

    row_nb = ctk.CTkFrame(inputs_section, fg_color="transparent")
    row_nb.pack(fill="x", pady=(0, 10))
    ctk.CTkLabel(row_nb, text="Sous-réseaux souhaités", width=150, anchor="w", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(side="left")
    vcmd_nb = (app.register(lambda val: val.isdecimal() and len(val) <= 7 or val == ""), "%P")
    entry_nb = ctk.CTkEntry(row_nb, width=120, height=36, justify="center", fg_color=COLORS["panel"], border_color=COLORS["border"], validate="key", validatecommand=vcmd_nb)
    entry_nb.pack(side="left")

    # -- Résultat: résumé + tableau des sous-réseaux ---------------------
    results = ctk.CTkFrame(card, fg_color=COLORS["panel"], border_width=1, border_color=COLORS["border"], corner_radius=12)
    results.pack(fill="x", padx=20, pady=(0, 14))

    result_label = ctk.CTkLabel(
        results, text="Saisis une IP et le nombre de sous-réseaux, puis clique sur Calculer.",
        font=("Segoe UI", 13), text_color=COLORS["muted"], justify="left", anchor="w", wraplength=820,
    )
    result_label.pack(fill="x", padx=16, pady=(12, 8))

    style = ttk.Style()
    style.configure("Decoupe.Treeview", background=COLORS["surface"], foreground=COLORS["text"], rowheight=24,
                    fieldbackground=COLORS["surface"], bordercolor=COLORS["border"], borderwidth=0, font=("Segoe UI", 10))
    style.configure("Decoupe.Treeview.Heading", background=COLORS["panel"], foreground=COLORS["text"],
                    relief="flat", font=("Segoe UI", 10, "bold"))

    zone_tableau = ctk.CTkFrame(results, fg_color="transparent")
    zone_tableau.pack(fill="x", padx=12, pady=(0, 12))

    colonnes = [("numero", "N°", 60), ("reseau", "Adresse réseau", 170), ("premier_hote", "Premier hôte", 170),
                ("dernier_hote", "Dernier hôte", 170), ("broadcast", "Broadcast", 170)]
    tableau = ttk.Treeview(zone_tableau, columns=[c[0] for c in colonnes], show="headings", height=8, style="Decoupe.Treeview")
    for cle, entete, largeur in colonnes:
        tableau.heading(cle, text=entete)
        tableau.column(cle, width=largeur, anchor="center", stretch=True)
    scrollbar = ttk.Scrollbar(zone_tableau, orient="vertical", command=tableau.yview)
    tableau.configure(yscrollcommand=scrollbar.set)
    tableau.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    zone_tableau.grid_columnconfigure(0, weight=1)

    # -- Historique (fonctionnalité 6 : entrées + dernier modificateur) --
    def recharger_depuis_historique(ligne):
        remplir_octets(entries_ip, ligne["reseau"])
        entry_nb.delete(0, "end")
        entry_nb.insert(0, str(ligne["nb_sous_reseaux"]))

    historique = creer_panneau_historique(
        card, "Historique des découpes enregistrées",
        [("reseau", "Réseau", 140), ("cidr", "CIDR de base", 90), ("nb_sous_reseaux", "Sous-réseaux demandés", 160),
         ("modifie_par", "Dernier modificateur", 150), ("modifie_le", "Le", 130)],
        lister_decoupes_sous_reseaux,
        recharger_depuis_historique,
    )

    def afficher_erreur(message: str) -> None:
        """Affiche un message d'erreur dans la zone de résultat et vide le tableau."""
        tableau.delete(*tableau.get_children())
        result_label.configure(text=message, text_color=COLORS["danger"])

    def on_calculer():
        """Lit l'IP et le nombre de sous-réseaux, calcule la découpe, l'enregistre puis l'affiche."""
        octets = lire_octets(entries_ip)
        if octets is None:
            afficher_erreur("IP invalide : chaque octet doit être un nombre entre 0 et 255.")
            return

        texte_nb = entry_nb.get().strip()
        if not texte_nb.isdecimal():
            afficher_erreur("Nombre de sous-réseaux invalide : saisis un nombre entier.")
            return

        try:
            decoupe = calculer_decoupe(octets, int(texte_nb))
        except ValueError as erreur:
            afficher_erreur(str(erreur))
            return

        # Fonctionnalité 6 : on stocke le réseau de base, son CIDR, le nombre demandé et le dernier modificateur
        if not enregistrer_decoupe_sous_reseaux(decoupe["adresse_reseau"], decoupe["cidr_base"], decoupe["nb_demande"],
                                                user_id, record_id=historique.id_selectionne()):
            messagebox.showwarning("Base de données", "Enregistrement impossible (voir la console).")
        historique.rafraichir()

        texte = (
            f"Classe {decoupe['classe']} - réseau {decoupe['adresse_reseau']}/{decoupe['cidr_base']} "
            f"(masque {decoupe['masque_base']})\n"
            f"Bits empruntés : {decoupe['bits_empruntes']}  ->  nouveau masque {decoupe['nouveau_masque']} (/{decoupe['nouveau_cidr']})\n"
            f"Sous-réseaux obtenus : {decoupe['nb_obtenus']} (demandés : {decoupe['nb_demande']})   |   "
            f"Hôtes utilisables par sous-réseau : {decoupe['hotes_par_sous_reseau']}"
        )
        if decoupe["nb_obtenus"] > LIMITE_LIGNES:
            texte += f"\nAffichage limité aux {LIMITE_LIGNES} premiers sous-réseaux."
        result_label.configure(text=texte, text_color=COLORS["primary"])

        tableau.delete(*tableau.get_children())
        for ligne in lister_sous_reseaux(decoupe):
            tableau.insert("", "end", values=[ligne[cle] for cle, _, _ in colonnes])

    def on_effacer():
        """Vide les champs, le résultat et quitte le mode modification de l'historique."""
        for entry in entries_ip:
            entry.delete(0, "end")
        entry_nb.delete(0, "end")
        tableau.delete(*tableau.get_children())
        result_label.configure(text="Saisis une IP et le nombre de sous-réseaux, puis clique sur Calculer.", text_color=COLORS["muted"])
        historique.reinitialiser()

    app.bind("<Return>", lambda _e: on_calculer())

    ctk.CTkButton(
        actions,
        text="Calculer",
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
        command=on_calculer,
    ).pack(side="left", expand=True, fill="x", padx=(0, 8))

    ctk.CTkButton(
        actions,
        text="Effacer",
        height=42,
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        font=("Segoe UI", 14, "bold"),
        command=on_effacer,
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
    create_decoupe_ui()
