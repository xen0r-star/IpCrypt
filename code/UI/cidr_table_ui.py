import csv
import customtkinter as ctk
from tkinter import filedialog, ttk

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


def center_window(window: ctk.CTk, width: int, height: int) -> None:
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    pos_x = int((screen_w - width) / 2)
    pos_y = int((screen_h - height) / 2)
    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


def binaire_decimal(mask_binary: str) -> str:
    octets = [mask_binary[i : i + 8] for i in range(0, 32, 8)]
    return ".".join(str(int(octet, 2)) for octet in octets)


def build_cidr_rows() -> list[tuple[str, str, str]]:
    rows = []
    for prefix in range(8, 31):
        mask_binary = "1" * prefix + "0" * (32 - prefix)
        dotted_binary = ".".join(mask_binary[i : i + 8] for i in range(0, 32, 8))
        rows.append((f"/{prefix}", dotted_binary, binaire_decimal(mask_binary)))
    return rows


app = ctk.CTk()
app.title("Tableau CIDR")
app.configure(fg_color=COLORS["bg"])
app.resizable(False, False)
center_window(app, 980, 700)

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
tree = ttk.Treeview(
    tree_container,
    columns=columns,
    show="headings",
    style="Cidr.Treeview",
)

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

status_var = ctk.StringVar(value="Pret a exporter le tableau CIDR")
ctk.CTkLabel(
    container,
    textvariable=status_var,
    font=("Segoe UI", 12),
    text_color=COLORS["muted"],
).pack(anchor="w", pady=(10, 0))


def export_table() -> None:
    file_path = filedialog.asksaveasfilename(
        title="Exporter le tableau CIDR",
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv"), ("Tous les fichiers", "*.*")],
        initialfile="tableau_cidr.csv",
    )

    if not file_path:
        status_var.set("Export annule")
        return

    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["CIDR", "Masque en binaire", "Masque en decimal"])
        writer.writerows(cidr_rows)

    status_var.set(f"Export termine: {file_path}")


actions = ctk.CTkFrame(container, fg_color="transparent")
actions.pack(fill="x", pady=(12, 0))

ctk.CTkButton(
    actions,
    text="Export",
    height=42,
    fg_color=COLORS["primary"],
    hover_color=COLORS["primary_hover"],
    font=("Segoe UI", 14, "bold"),
    command=export_table,
).pack(side="left", expand=True, fill="x", padx=(0, 8))

ctk.CTkButton(
    actions,
    text="Exit",
    height=42,
    fg_color=COLORS["danger"],
    hover_color=COLORS["danger_hover"],
    font=("Segoe UI", 14, "bold"),
    command=app.destroy,
).pack(side="left", fill="x", padx=(8, 0))

app.mainloop()
