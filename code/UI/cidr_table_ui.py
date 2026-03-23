import os
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#f4f6fb",
    "surface": "#ffffff",
    "panel": "#f9fbff",
    "primary": "#2f6fed",
    "primary_hover": "#2459c9",
    "danger": "#d94848",
    "danger_hover": "#b93a3a",
    "text": "#17233a",
    "muted": "#5b6b84",
    "border": "#d7deea",
}

# Fonction pour centrer la fenêtre sur l'écran
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

#ouverture d'une fenêtre de dialogue pour choisir le dossier de destination du fichier Excel
def exporterTableau(tableauSR):
    
    try:
        # Ouvre une boîte de dialogue pour choisir le nom et l'emplacement
        chemin = filedialog.asksaveasfilename(
        title="Enregistrer le fichier Excel",
        initialfile="TableauMasques.xlsx",  # Nom par défaut
        defaultextension=".xlsx",
        filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")]
)

        if not chemin:
            messagebox.showwarning("Annulé", "Aucun dossier sélectionné.")
            return None

        df = pd.DataFrame(tableauSR, columns=["CIDR", "Masque en Binaire", "Masque en décimal"])
        with pd.ExcelWriter(os.path.join(chemin, "TableauMasques.xlsx"), engine="xlsxwriter") as fichier:
            df.to_excel(fichier, sheet_name="Matrice des sous réseaux", index=False)

        print(f"Le fichier a été généré avec succès à l'emplacement suivant : {os.path.join(chemin, 'TableauMasques.xlsx')}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
        return None
        
#transformation du masque binaire en décimal pour l'affichage dans le tableau et l'exportation
def binaireDecimal(masqueBinaire):
    octets = [masqueBinaire[i:i+8] for i in range(0, 32, 8)]
    return ".".join([str(int(o, 2)) for o in octets])

#construction du tableau CIDR pour l'affichage dans l'interface et l'exportation
def build_cidr_rows() -> list:
    matSR = []
    for index in range(8, 31):
        cidr = "/" + str(index)
        masqueBinaire = "1" * index + "0" * (32 - index)
        masqueDecimal = binaireDecimal(masqueBinaire)
        for point in range(24, 0, -8):
            masqueBinaire = masqueBinaire[:point] + "." + masqueBinaire[point:]
        matSR.append([cidr, masqueBinaire, masqueDecimal])
    return matSR

# Création de l'interface pour le tableau CIDR
def create_cidr_table_ui(on_back=None):
    app = ctk.CTk()
    next_action = None
    app.title("Tableau CIDR")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(False, False)
    center_window(app, 980, 700)

    def schedule_navigation(callback, *args, **kwargs):
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=28, pady=20)

    ctk.CTkLabel(
        container,
        text="Tableau CIDR",
        font=("Segoe UI", 34, "bold"),
        text_color=COLORS["text"],
    ).pack(anchor="center")

    ctk.CTkLabel(
        container,
        text="Visualise et exporte la matrice des masques",
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
    card.pack(fill="both", expand=True)

    table_frame = ctk.CTkFrame(
        card,
        fg_color=COLORS["panel"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=12,
    )
    table_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
    tree_container.pack(fill="both", expand=True, padx=12, pady=12)

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Cidr.Treeview",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=28,
        fieldbackground=COLORS["surface"],
        bordercolor=COLORS["border"],
        borderwidth=0,
        font=("Segoe UI", 11),
    )
    style.configure(
        "Cidr.Treeview.Heading",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        relief="flat",
        font=("Segoe UI", 11, "bold"),
    )

    columns = ("cidr", "binary", "decimal")
    tree = ttk.Treeview(tree_container, columns=columns, show="headings", style="Cidr.Treeview")

    tree.heading("cidr", text="CIDR")
    tree.heading("binary", text="Masque en binaire")
    tree.heading("decimal", text="Masque en decimal")

    tree.column("cidr", width=110, anchor="center")
    tree.column("binary", width=460, anchor="center")
    tree.column("decimal", width=220, anchor="center")

    scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree_container.grid_columnconfigure(0, weight=1)
    tree_container.grid_rowconfigure(0, weight=1)

    cidr_rows = build_cidr_rows()
    for row in cidr_rows:
        tree.insert("", "end", values=row)

    ctk.CTkLabel(
        container,
        text="Pret a exporter le tableau CIDR",
        font=("Segoe UI", 12),
        text_color=COLORS["muted"],
    ).pack(anchor="w", pady=(10, 0))

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(12, 0))

    ctk.CTkButton(
        actions,
        text="Export",
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
        command=lambda: exporterTableau(cidr_rows),
    ).pack(side="left", expand=True, fill="x", padx=(0, 8))

    ctk.CTkButton(
        actions,
        text="Retour menu",
        height=42,
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        font=("Segoe UI", 14, "bold"),
        command=(lambda: schedule_navigation(on_back) if callable(on_back) else app.quit()),
    ).pack(side="left", fill="x", padx=(8, 0))

    app.mainloop()
    cleanup_window(app)
    if callable(next_action):
        next_action()

if __name__ == "__main__":
    create_cidr_table_ui()