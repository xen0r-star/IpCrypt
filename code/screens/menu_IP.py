import customtkinter as ctk

from pathlib import Path
ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#eef1f6",
    "surface": "#ffffff",
    "primary": "#3f5fa8",
    "primary_hover": "#355190",
    # "danger": "#d9484897",
    # "danger_hover": "#b93a3a",
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
    # CustomTkinter laisse des callbacks after() en vie (animations, DPI checks).
    # Si on détruit la fenêtre sans les annuler, Tk fire sur des widgets morts
    # → TclError "invalid command name". On draine d'abord, puis destroy.
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


def create_menu_ip_ui(
    on_open_subnet_verification=None,
    on_open_definer_classe=None,
    on_open_get_mask=None,
    on_open_get_network=None,
    on_back=None,
    is_admin=False,
):
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("Gestion adresse IP")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(True, True)
    center_window(app, 720, 520)

    # Pattern de navigation différée : on stocke le callback, on quitte mainloop,
    # cleanup_window() s'exécute, puis on appelle le callback dans un contexte propre.
    # Appeler le callback directement ici planterait car mainloop() n'est pas terminé.
    def schedule_navigation(callback, *args, **kwargs):
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=28, pady=20)

    ctk.CTkLabel(
        container,
        text="Menu principal",
        font=("Segoe UI", 34, "bold"),
        text_color=COLORS["text"],
    ).pack(anchor="center")

    ctk.CTkLabel(
        container,
        text="Sélectionne un module puis ouvre-le",
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

    modules = [
        "IP Vérification",
        "Recherche classe IP",
        "Recherche masque IP",
        "Définir réseau et sous réseau",
    ]
    # "Inscription" visible seulement pour les admins — inséré en tête pour mise en évidence.
    if is_admin:
        modules.insert(0, "Inscription")

    modules_var = ctk.StringVar(value=modules[0])

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
            fg_color="#f4f6f9",
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

    def on_open_selected_module():
        selected = modules_var.get()
        # Table de dispatch : évite une chaîne if/elif fragile à l'ajout de modules.
        routes = {
            "IP Vérification": on_open_subnet_verification,
            "Recherche classe IP": on_open_definer_classe,
            "Recherche masque IP": on_open_get_mask,
            "Définir réseau et sous réseau": on_open_get_network,
        }
        callback = routes.get(selected)
        if callable(callback):
            schedule_navigation(callback)

    actions = ctk.CTkFrame(container, fg_color="transparent")
    actions.pack(fill="x", pady=(14, 0))

    ctk.CTkButton(
        actions,
        text="Ouvrir le module",
        height=42,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=("Segoe UI", 14, "bold"),
        command=on_open_selected_module,
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
    create_menu_ip_ui()
