import customtkinter as ctk

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
}

def center_window(window: ctk.CTk, width: int, height: int) -> None:
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    pos_x = int((screen_w - width) / 2)
    pos_y = int((screen_h - height) / 2)
    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


app = ctk.CTk()
app.title("Menu principal")
app.configure(fg_color=COLORS["bg"])
app.resizable(False, False)
center_window(app, 720, 520)

container = ctk.CTkFrame(app, fg_color="transparent")
container.pack(fill="both", expand=True, padx=28, pady=20)

#style donne via customtkinter, pas besoin de faire du css ou du ttk"
ctk.CTkLabel(
    container,
    text="Menu principal",
    font=("Segoe UI", 34, "bold"),
    text_color=COLORS["text"],
).pack(anchor="center")

ctk.CTkLabel(
    container,
    text="Selectionne un module puis ouvre-le",
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

modules_var = ctk.StringVar(value="IP Verification")
modules = [
    "IP Verification",
    "IP Association",
    "Inscription",
    "CIDR Table",
]

module_list = ctk.CTkFrame(card, fg_color="transparent")
module_list.pack(fill="both", expand=True, padx=22, pady=20)

ctk.CTkLabel(
    module_list,
    text="Modules disponibles",
    font=("Segoe UI", 14, "bold"),
    text_color=COLORS["text"],
).pack(anchor="w", pady=(0, 10))

for module_name in modules:
    row = ctk.CTkFrame(
        module_list,
        fg_color="#f9fbff",
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=10,
    )
    row.pack(fill="x", pady=6)

    ctk.CTkRadioButton(
        row,
        text=module_name,
        variable=modules_var,
        value=module_name,
        font=("Segoe UI", 13),
        text_color=COLORS["text"],
    ).pack(anchor="w", padx=12, pady=10)

actions = ctk.CTkFrame(container, fg_color="transparent")
actions.pack(fill="x", pady=(14, 0))

ctk.CTkButton(
    actions,
    text="Ouvrir le module",
    height=42,
    fg_color=COLORS["primary"],
    hover_color=COLORS["primary_hover"],
    font=("Segoe UI", 14, "bold"),
).pack(side="left", expand=True, fill="x", padx=(0, 8))

ctk.CTkButton(
    actions,
    text="Quitter",
    height=42,
    fg_color=COLORS["danger"],
    hover_color=COLORS["danger_hover"],
    font=("Segoe UI", 14, "bold"),
    command=app.destroy,
).pack(side="left", fill="x", padx=(8, 0))

app.mainloop()