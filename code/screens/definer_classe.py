import customtkinter as ctk

from pathlib import Path
ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

def definirClasse(premOctet):
    octet=int(premOctet)
    match octet:
        case _ if 1 <= octet <= 126:
            print("Classe A")
            return "A"
        case _ if 128 <= octet <= 191:
            print("Classe B")
            return "B"
        case _ if 192 <= octet <= 223:
            print("Classe C")
            return "C"
        case _ if 224 <= octet <= 240:
            print("Classe D")
            return "D"
        case _:
            print("Classe E")
            return "E"

def definirTypeIP(octets):
    o1, o2 = int(octets[0]), int(octets[1])
    
    if o1 == 10: return "Privée"
    if o1 == 172 and 16 <= o2 <= 31: return "Privée"
    if o1 == 192 and o2 == 168: return "Privée"
    if o1 == 127: return "Réservée (Loopback)"
    if o1 == 169 and o2 == 254: return "Réservée (APIPA)"
    
    return "Publique"

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

group_entries = []

def ip_octet_group(parent: ctk.CTkFrame, label_text: str) -> None:
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

    vcmd = (parent.winfo_toplevel().register(lambda val: val.isdigit() and len(val) <= 3 or val == ""), "%P")
    
    for i in range(4):
        entry = ctk.CTkEntry(inner, width=55, height=36, justify="center", fg_color=COLORS["surface"], border_color=COLORS["border"], validate="key", validatecommand=vcmd)
        entry.pack(side="left")
        group_entries.append(entry)
        if i < 3:
            ctk.CTkLabel(inner, text=".", font=("Segoe UI", 18, "bold"), text_color=COLORS["muted"]).pack(side="left", padx=6)

result_labels = {}

def lire_octets(group: list) -> list | None:
    """Extrait et valide les 4 octets d'un groupe de champs Entry."""
    octets = []
    for entry in group:
        val = entry.get().strip()
        if not val.isdigit() or not (0 <= int(val) <= 255):
            return None
        octets.append(str(int(val)).zfill(3))
    return octets
    
def create_definer_class_ui(on_back=None):
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("IP Verification")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(True, True)
    center_window(app, 600, 450)

    def schedule_navigation(callback, *args, **kwargs):
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="x", padx=28, pady=20) 

    ctk.CTkLabel(
        container,
        text="IP Verification",
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

    results = ctk.CTkFrame(
        card,
        fg_color=COLORS["panel"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=12,
    )
    results.pack(fill="x", padx=20, pady=(0, 20)) 

    fields = [
        "Classe du réseau",
        "Type d'adresse"
    ]

    for label_text in fields:
        row = ctk.CTkFrame(results, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=5)
        
        ctk.CTkLabel(row, text=label_text + " :", width=180, anchor="e", 
                     font=("Segoe UI", 13), text_color=COLORS["text"]).pack(side="left")
        
        # On crée le label de valeur
        val_label = ctk.CTkLabel(row, text="-", anchor="w", 
                                 font=("Segoe UI", 13, "bold"), text_color=COLORS["muted"])
        val_label.pack(side="left", padx=10)
        
        # CRUCIAL : On enregistre le widget dans le dictionnaire pour le modifier plus tard
        result_labels[label_text] = val_label

    def on_verify():
    # On utilise directement notre liste all_entries
        octets = lire_octets(group_entries)
        classeAdresse = "N/A"
        typeAdresse = "N/A"
        
        if octets:
            classe = definirClasse(octets[0])
            typeAdresse = definirTypeIP(octets)

            # Mise à jour des labels via le dictionnaire
            result_labels["Classe du réseau"].configure(text=classe, text_color=COLORS["primary"])
            result_labels["Type d'adresse"].configure(text=typeAdresse, text_color=COLORS["primary"])
            # ... continue pour les autres champs
        else:
            # Optionnel : Message d'erreur si IP invalide
            result_labels["Classe du réseau"].configure(text="IP Invalide", text_color=COLORS["danger"])
            result_labels["Type d'adresse"].configure(text="IP Invalide", text_color=COLORS["danger"])

        

    def on_clear():
        def clear_recursive(container):
            for widget in container.winfo_children():
                # Si c'est un champ de saisie, on l'efface
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                # Si c'est un cadre, on regarde à l'intérieur
                elif isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                    clear_recursive(widget)
        clear_recursive(inputs_section)
        # Reset les labels de résultats ici si besoin
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
    create_definer_class_ui()