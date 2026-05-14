import os
import csv
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

try:
    import pandas as pd
    _PANDAS_AVAILABLE = True
except Exception:
    # Sur certains Windows, le contrôle applicatif bloque les DLL natives de pandas.
    pd = None
    _PANDAS_AVAILABLE = False

ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ══════════════════════════════════════════════
# Logique métier
# ══════════════════════════════════════════════

def binaireDecimal(masqueBinaire):
    """Convertit un masque binaire 32 bits (sans points) en notation décimale pointée."""
    octets = [masqueBinaire[i:i+8] for i in range(0, 32, 8)]
    return ".".join([str(int(o, 2)) for o in octets])


def build_cidr_rows() -> list:
    """Génère les lignes de la matrice CIDR pour les préfixes /8 à /30 : [notation CIDR, masque binaire, masque décimal]."""
    matSR = []
    for index in range(8, 31):
        cidr = "/" + str(index)
        masqueBinaire = "1" * index + "0" * (32 - index)
        masqueDecimal = binaireDecimal(masqueBinaire)
        for point in range(24, 0, -8):
            masqueBinaire = masqueBinaire[:point] + "." + masqueBinaire[point:]
        matSR.append([cidr, masqueBinaire, masqueDecimal])
    return matSR


def exporterTableau(tableauSR):
    """Exporte la matrice CIDR en fichier Excel (.xlsx via pandas) ou CSV si pandas est indisponible."""
    try:
        if _PANDAS_AVAILABLE:
            chemin = filedialog.asksaveasfilename(
                title="Enregistrer le fichier Excel",
                initialfile="TableauMasques.xlsx",
                defaultextension=".xlsx",
                filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
            )
        else:
            chemin = filedialog.asksaveasfilename(
                title="Enregistrer le fichier CSV",
                initialfile="TableauMasques.csv",
                defaultextension=".csv",
                filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            )

        if not chemin:
            return None

        if _PANDAS_AVAILABLE:
            df = pd.DataFrame(tableauSR, columns=["Préfixe CIDR", "Masque binaire", "Masque décimal"])
            with pd.ExcelWriter(chemin, engine="xlsxwriter") as fichier:
                df.to_excel(fichier, sheet_name="Matrice des sous-réseaux", index=False)
            print(f"Le fichier a été généré avec succès à l'emplacement suivant : {chemin}")
        else:
            with open(chemin, "w", newline="", encoding="utf-8") as fichier:
                writer = csv.writer(fichier)
                writer.writerow(["Préfixe CIDR", "Masque binaire", "Masque décimal"])
                writer.writerows(tableauSR)
            messagebox.showinfo(
                "Export CSV",
                "Pandas est indisponible (DLL bloquée). Export réalisé en CSV.",
            )
            print(f"Le fichier CSV a été généré avec succès à l'emplacement suivant : {chemin}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
        return None


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


def create_cidr_table_ui(on_back=None):
    """Fenêtre Tableau CIDR : affiche la matrice des masques /8 à /30 et permet l'export Excel ou CSV."""
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("Tableau CIDR")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(True, True)
    center_window(app, 960, 680)

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
        font=("Segoe UI", 14, "bold"),
    )

    columns = ("cidr", "binary", "decimal")
    tree = ttk.Treeview(tree_container, columns=columns, show="headings", style="Cidr.Treeview")

    tree.heading("cidr", text="Préfixe CIDR")
    tree.heading("binary", text="Masque binaire")
    tree.heading("decimal", text="Masque décimal")

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
        text=("Prêt à exporter le tableau CIDR (Excel)" if _PANDAS_AVAILABLE else "Prêt à exporter le tableau CIDR (CSV)"),
        font=("Segoe UI", 12),
        text_color=COLORS["muted"],
    ).pack(anchor="w", pady=(10, 0))

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(12, 0))

    ctk.CTkButton(
        actions,
        text=("Export Excel" if _PANDAS_AVAILABLE else "Export CSV"),
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
        command=lambda: exporterTableau(cidr_rows),
    ).pack(side="left", expand=True, fill="x", padx=(0, 8))

    ctk.CTkButton(
        actions,
        text="Retour au menu",
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
