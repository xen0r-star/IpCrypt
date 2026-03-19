import customtkinter as ctk

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

    for i in range(4):
        ctk.CTkEntry(inner, width=55, height=36, justify="center", fg_color=COLORS["surface"], border_color=COLORS["border"]).pack(side="left")
        if i < 3:
            ctk.CTkLabel(inner, text=".", font=("Segoe UI", 18, "bold"), text_color=COLORS["muted"]).pack(side="left", padx=6)

def create_ip_association_ui():
    app = ctk.CTk()
    app.title("IP Association")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(False, False)
    center_window(app, 900, 730)

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=28, pady=20)

    ctk.CTkLabel(
        container,
        text="IP Association",
        font=("Segoe UI", 34, "bold"),
        text_color=COLORS["text"],
    ).pack(anchor="center")

    ctk.CTkLabel(
        container,
        text="Compare deux adresses IP et determine si elles sont dans le meme reseau ou pas",
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

    section_1 = ctk.CTkFrame(
        card,
        fg_color=COLORS["panel"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=12,
    )
    section_1.pack(fill="x", padx=20, pady=(18, 10))
    ctk.CTkLabel(section_1, text="Adresse 1", font=("Segoe UI", 14, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(12, 8))
    ip_octet_group(section_1, "IP 1")
    ip_octet_group(section_1, "Masque 1")

    section_2 = ctk.CTkFrame(
        card,
        fg_color=COLORS["panel"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=12,
    )
    section_2.pack(fill="x", padx=20, pady=(0, 14))
    ctk.CTkLabel(section_2, text="Adresse 2", font=("Segoe UI", 14, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(12, 8))
    ip_octet_group(section_2, "IP 2")
    ip_octet_group(section_2, "Masque 2")

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(14, 0))

    ctk.CTkButton(
        actions,
        text="Associer",
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
    ).pack(side="left", expand=True, fill="x", padx=(0, 8))

    ctk.CTkButton(
        actions,
        text="Effacer",
        height=42,
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        font=("Segoe UI", 14, "bold"),
    ).pack(side="left", fill="x", padx=(8, 0))

    app.mainloop()

create_ip_association_ui()