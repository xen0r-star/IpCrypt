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
    "field_bg": "#f9fbff",
}

SPACING = {
    "outer_x": 28,
    "outer_y": 20,
    "inner": 14,
}


def center_window(window: ctk.CTk, width: int, height: int) -> None:
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    pos_x = int((screen_w - width) / 2)
    pos_y = int((screen_h - height) / 2)
    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


app = ctk.CTk()
app.title("Connexion")
app.configure(fg_color=COLORS["bg"])
app.resizable(False, False)
center_window(app, 560, 430)

container = ctk.CTkFrame(app, fg_color="transparent")
container.pack(fill="both", expand=True, padx=SPACING["outer_x"], pady=SPACING["outer_y"])

ctk.CTkLabel(
    container,
    text="Connexion",
    font=("Segoe UI", 34, "bold"),
    text_color=COLORS["text"],
).pack(anchor="center")

ctk.CTkLabel(
    container,
    text="Accede a ton espace reseau",
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
card.pack(fill="x", padx=2, pady=(0, 16))

form = ctk.CTkFrame(card, fg_color="transparent")
form.pack(fill="x", padx=20, pady=18)

ctk.CTkLabel(form, text="Nom utilisateur", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
ctk.CTkEntry(form, height=40, fg_color=COLORS["field_bg"], border_color=COLORS["border"]).pack(fill="x", pady=(6, 12))

ctk.CTkLabel(form, text="Mot de passe", font=("Segoe UI", 13, "bold"), text_color=COLORS["text"]).pack(anchor="w")
ctk.CTkEntry(form, height=40, show="*", fg_color=COLORS["field_bg"], border_color=COLORS["border"]).pack(fill="x", pady=(6, 10))
ctk.CTkCheckBox(form, text="Afficher le mot de passe", text_color=COLORS["muted"]).pack(anchor="w")

actions = ctk.CTkFrame(container, fg_color="transparent")
actions.pack(fill="x")

ctk.CTkButton(
    actions,
    text="Se connecter",
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
