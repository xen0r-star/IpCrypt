import customtkinter as ctk

from pathlib import Path
ICO = Path(__file__).resolve().parent.parent / "images" / "iconeIpCrypt.ico"

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


def create_menu_ui(
    on_open_ip_verification=None,
    on_open_ip_association=None,
    on_open_inscription=None,
    on_open_cidr_table=None,
    on_logout=None,
    is_admin=False,
):
    app = ctk.CTk()
    if ICO.exists():
        app.after(100, lambda: app.iconbitmap(str(ICO)))
    next_action = None
    app.title("Menu principal")
    app.configure(fg_color=COLORS["bg"])
    app.resizable(False, False)
    center_window(app, 720, 520)

    def schedule_navigation(callback, *args, **kwargs):
        nonlocal next_action
        if callable(callback):
            next_action = lambda: callback(*args, **kwargs)
        app.quit()

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

    modules = [
        "IP Verification",
        "IP Association",
        "CIDR Table",
    ]
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

    def on_open_selected_module():
        selected = modules_var.get()
        routes = {
            "IP Verification": on_open_ip_verification,
            "IP Association": on_open_ip_association,
            "Inscription": on_open_inscription,
            "CIDR Table": on_open_cidr_table,
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
        text="Deconnexion",
        height=42,
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        font=("Segoe UI", 14, "bold"),
        command=(lambda: schedule_navigation(on_logout) if callable(on_logout) else app.quit()),
    ).pack(side="left", fill="x", padx=(8, 0))

    app.mainloop()
    cleanup_window(app)
    if callable(next_action):
        next_action()


if __name__ == "__main__":
    create_menu_ui()