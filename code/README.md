<div align="center">

# IpCrypt

Desktop network tool — Python + CustomTkinter.
IP verification, subnet analysis, cross-network association, CIDR table, user management.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-2CA5E0?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Phase%201-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-Academic-lightgrey?style=for-the-badge)

</div>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#modules">Modules</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Modules](#modules)
- [Password Policy](#password-policy)
- [Roadmap](#roadmap)

---

## About

IpCrypt is a Python desktop application built for the BAC2 Systems & Networks curriculum.
It provides a GUI-first approach to common IP addressing tasks — class detection, subnet calculation, cross-network visibility, and CIDR table generation — all without relying on any Python networking library (`ipaddress`, `socket`, etc.).

User access is controlled via login (admin / client profiles). Accounts and hashed passwords are persisted in a flat file. Admins get access to the user registration module.

---

## Features

| Module | Status | Description |
|---|---|---|
| Splash screen | Done | Animated loading screen on startup |
| Login | Done | Username + password with policy enforcement |
| Registration | Done | Admin-only user creation with profile selection |
| Menu | Done | Role-aware navigation (admin vs client) |
| IP Verification | In progress | Class, reserved/private flags, broadcast, host range |
| IP Association | Done | Bilateral cross-network visibility check |
| CIDR Table | Done | /8–/30 matrix with binary + decimal + Excel export |

---

## Architecture

The app uses a **sequential window model**: each screen is a `ctk.CTk()` instance that calls `mainloop()`, cleans up, then invokes a navigation callback to open the next screen. No multi-threading, no persistent root window.

```
main.py
  └─ show_splash()          # tkinter splash
  └─ launch()
       ├─ open_connexion()  ──► connexion_ui.py   → on_login_success=open_menu
       ├─ open_inscription()──► inscription_ui.py → on_back=open_menu|open_connexion
       ├─ open_menu()       ──► menu_ui.py        → routes to modules
       ├─ open_ip_verification() ──► ip_verification_ui.py
       ├─ open_ip_association()  ──► ip_association_ui.py
       └─ open_cidr_table()      ──► cidr_table_ui.py
```

Navigation flow:

```
Splash → Connexion → Menu ──┬── IP Verification ──┐
                             ├── IP Association   ──┤→ Menu
                             ├── CIDR Table       ──┘
                             └── Inscription (admin only) → Menu
```

---

## Project Structure

```text
IpCrypt/
├── main.py
├── UI/
│   ├── connexion_ui.py
│   ├── inscription_ui.py
│   ├── menu_ui.py
│   ├── ip_verification_ui.py
│   ├── ip_association_ui.py
│   └── cidr_table_ui.py
├── utils/
│   └── password_policy.py
├── data/
│   └── users.csv              # flat file — hashed credentials
├── images/
│   ├── iconeIpCrypt.ico
│   ├── menuIpCrypt.ico
│   └── menuIpCrypt.png        # splash image
└── requirements.txt
```

---

## Tech Stack

- **Python 3.10+**
- **CustomTkinter 5.x** — themed widgets
- **Pillow** — splash screen image rendering
- **pandas + xlsxwriter** — CIDR table Excel export
- **bcrypt** or **argon2-cffi** — password hashing (in progress)
- No IP networking library used — all calculations are manual bit operations

---

## Quick Start

### 1. Clone

```bash
git clone <repo-url>
cd IpCrypt
```

### 2. Virtual environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install customtkinter pillow pandas xlsxwriter bcrypt
```

### 4. Run

```bash
python main.py
```

---

## Modules

### Login (`connexion_ui.py`)

- Username (min 3 chars) + password fields
- Password show/hide toggle
- On success: detects admin profile from username, routes to menu

### Registration (`inscription_ui.py`)

- Accessible from menu by admin only
- Profile selector: Client / Admin
- Writes new user to flat file with hashed password

### Menu (`menu_ui.py`)

- Radio-button module selector
- Admin view: Inscription, IP Verification, IP Association, CIDR Table
- Client view: IP Verification, IP Association, CIDR Table

### IP Verification (`ip_verification_ui.py`)

- Octet-by-octet input with validation (0–255)
- Outputs: IP class, reserved/private flag, class mask, network address, broadcast, first/last host, host count
- Status: UI done, business logic in progress

### IP Association (`ip_association_ui.py`)

- Two IP + mask pairs (octet groups)
- AND-based network address calculation
- Bilateral check: A sees B / B sees A / mutual / none
- Results displayed inline

### CIDR Table (`cidr_table_ui.py`)

- Generates /8 to /30 (23 rows)
- Columns: CIDR notation, binary mask (dotted), decimal mask
- Export to `.xlsx` via file dialog

---

## Password Policy

Enforced at both login and registration via `utils/password_policy.py`:

| Rule | Value |
|---|---|
| Minimum length | 12 characters |
| Minimum uppercase | 2 |
| Minimum digits | 1 |
| Minimum special chars | 1 |

The validator is parametric — thresholds can be adjusted per call site.

---

## Roadmap

- [ ] Wire IP Verification business logic (class detection, broadcast, host range)
- [ ] Integrate flat file read/write for user persistence
- [ ] Implement password hashing (bcrypt or argon2) on registration + verification on login
- [ ] Input validation on IP Verification (currently no octet validation)
- [ ] Centralize shared UI constants (`COLORS`, `center_window`, `cleanup_window`) into a `ui_shared.py` module
- [ ] Unit tests for network calculation functions
- [ ] Add IP class mask deduction (classfull)
- [ ] Restrict admin access enforcement beyond UI (server-side check on flat file)

---

## Author

Project built as part of the BAC2 SR curriculum — Phase 1.
