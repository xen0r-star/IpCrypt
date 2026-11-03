from types import SimpleNamespace
from tkinter import ttk

import customtkinter as ctk

# ══════════════════════════════════════════════
# Panneau « Historique » partagé par les écrans de fonctionnalités (F2 à F6).
# ══════════════════════════════════════════════

COLORS = {
    "bg": "#eef1f6",
    "surface": "#ffffff",
    "panel": "#f6f8fc",
    "primary": "#3f5fa8",
    "text": "#16233b",
    "muted": "#5a6b86",
    "border": "#cfd8e6",
}

TEXTE_NOUVEAU = "Mode : nouvel enregistrement"


def remplir_octets(entries: list, texte: str) -> None:
    """Remplit un groupe de 4 champs Entry à partir d'une IP/masque en texte (ex. '10.0.0.1'). Les octets manquants restent vides."""
    parties = str(texte).split(".")
    for i, entry in enumerate(entries):
        entry.delete(0, "end")
        valeur = parties[i].strip() if i < len(parties) else ""
        if valeur:
            entry.insert(0, valeur)


def _formater(valeur) -> str:
    """Texte affiché dans une cellule : vide pour None, 'jj/mm/aaaa hh:mm' pour une date, str() sinon."""
    if valeur is None:
        return ""
    if hasattr(valeur, "strftime"):
        return valeur.strftime("%d/%m/%Y %H:%M")
    return str(valeur)


def creer_panneau_historique(parent, titre: str, colonnes: list, charger, on_select, hauteur: int = 4):
    """
    Crée le panneau et le place dans parent
      - colonnes : [(id_colonne, en-tête, largeur), ...]
      - charger() : retourne une liste de dict contenant au minimum la clé 'id' (voir data_service.lister_*)
      - on_select(ligne) : appelé quand l'utilisateur clique une ligne (pour remplir les champs de saisie)
    Retourne un objet avec : rafraichir(), id_selectionne(), reinitialiser().
    """
    etat = {"id": None}

    cadre = ctk.CTkFrame(parent, fg_color=COLORS["panel"], border_width=1, border_color=COLORS["border"], corner_radius=12)
    cadre.pack(fill="x", padx=20, pady=(0, 20))

    ctk.CTkLabel(cadre, text=titre, font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(10, 0))
    label_mode = ctk.CTkLabel(cadre, text=TEXTE_NOUVEAU, font=("Segoe UI", 11), text_color=COLORS["muted"])
    label_mode.pack(anchor="w", padx=16)

    zone = ctk.CTkFrame(cadre, fg_color="transparent")
    zone.pack(fill="x", padx=12, pady=(6, 12))

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Historique.Treeview",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=24,
        fieldbackground=COLORS["surface"],
        bordercolor=COLORS["border"],
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Historique.Treeview.Heading",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        relief="flat",
        font=("Segoe UI", 10, "bold"),
    )

    cles = [colonne[0] for colonne in colonnes]
    tree = ttk.Treeview(zone, columns=cles, show="headings", height=hauteur, style="Historique.Treeview", selectmode="browse")
    for cle, entete, largeur in colonnes:
        tree.heading(cle, text=entete)
        tree.column(cle, width=largeur, anchor="center", stretch=True)

    scrollbar = ttk.Scrollbar(zone, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    zone.grid_columnconfigure(0, weight=1)

    lignes = {}

    def reinitialiser() -> None:
        """Quitte le mode modification (le prochain enregistrement créera une nouvelle ligne)."""
        etat["id"] = None
        label_mode.configure(text=TEXTE_NOUVEAU, text_color=COLORS["muted"])
        tree.selection_remove(*tree.selection())

    def rafraichir() -> None:
        """Recharge la liste depuis la base et quitte le mode modification."""
        lignes.clear()
        tree.delete(*tree.get_children())
        for ligne in charger():
            iid = str(ligne["id"])
            lignes[iid] = ligne
            tree.insert("", "end", iid=iid, values=[_formater(ligne.get(cle)) for cle in cles])
        etat["id"] = None
        label_mode.configure(text=TEXTE_NOUVEAU, text_color=COLORS["muted"])

    def on_tree_select(_event=None) -> None:
        selection = tree.selection()
        if not selection or selection[0] not in lignes:
            return
        ligne = lignes[selection[0]]
        etat["id"] = ligne["id"]
        label_mode.configure(
            text=f"Mode : modification de l'enregistrement n°{ligne['id']} (Effacer pour annuler)",
            text_color=COLORS["primary"],
        )
        on_select(ligne)

    tree.bind("<<TreeviewSelect>>", on_tree_select)
    rafraichir()

    return SimpleNamespace(rafraichir=rafraichir, id_selectionne=lambda: etat["id"], reinitialiser=reinitialiser)
