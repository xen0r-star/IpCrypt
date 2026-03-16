<div align="center">

# IpCrypt
Network tool desktop app built with Python &amp; CustomTkinter. Features IP verification, subnet info, cross-network IP association and user management.

### Network Interface in Python + CustomTkinter

Desktop app prototype focused on IP addressing and subnet-related modules.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-UI-2CA5E0?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Prototype-orange?style=for-the-badge)

</div>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#run-the-ui-screens">Run the UI Screens</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## Table of Contents

- [About](#about)
- [Visual Preview](#visual-preview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Run the UI Screens](#run-the-ui-screens)
- [Notes](#notes)
- [Roadmap](#roadmap)

## About

This repository contains the graphical interfaces of a Python networking project.
The app is currently split into standalone screens (menu, login, registration, IP verification, IP association).

The current goal is to provide a clean, modern, and reusable UI foundation before full business logic integration.

## Visual Preview

You can replace these placeholders once your assets are ready.

### Demo GIF

![Demo GIF](assets/demo.gif)

### Screenshots

| Screen          | Preview                                                    |
| --------------- | ---------------------------------------------------------- |
| Main Menu       | ![Menu](assets/screenshots/menu.png)                       |
| Login           | ![Login](assets/screenshots/connexion.png)                 |
| Registration    | ![Registration](assets/screenshots/inscription.png)        |
| IP Verification | ![IP Verification](assets/screenshots/ip_verification.png) |
| IP Association  | ![IP Association](assets/screenshots/ip_association.png)   |

### Recommended File Layout

- `assets/demo.gif`
- `assets/screenshots/menu.png`
- `assets/screenshots/connexion.png`
- `assets/screenshots/inscription.png`
- `assets/screenshots/ip_verification.png`
- `assets/screenshots/ip_association.png`

## Features

- User login screen
- Registration screen with profile selection
- Main module navigation screen
- `IP Verification` module (IP/mask input + network result fields)
- `IP Association` module (comparison of two IP+mask pairs)
- Consistent visual theme (light mode, shared palette)

## Project Structure

```text
Projet-Phase1/
|- code/
|  |- connexion_ui.py
|  |- inscription_ui.py
|  |- menu_ui.py
|  |- ip_verification_ui.py
|  |- ip_association_ui.py
|  `- code-testtkinter.py
|- .venv/
`- README.md
```

## Tech Stack

- Python 3.10+
- CustomTkinter
- Tkinter (legacy test file)

## Quick Start

### 1) Clone the repository

```bash
git clone <url-du-repo>
cd Projet-Phase1
```

### 2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install customtkinter
```

Optional (freeze dependencies):

```bash
pip freeze > requirements.txt
```

## Run the UI Screens

From the project root:

```bash
python code/menu_ui.py
python code/connexion_ui.py
python code/inscription_ui.py
python code/ip_verification_ui.py
python code/ip_association_ui.py
```

## Notes

- The screens are currently UI prototypes (without full business logic).
- Main action buttons are in place and ready to be wired.
- `code-testtkinter.py` is kept as a legacy Tkinter draft.

## Roadmap

- Wire buttons to real actions
- Add input validation for IP and subnet mask fields
- Integrate network calculations (CIDR, broadcast, host range)
- Add unit tests
- Centralize shared UI constants in a dedicated module

---

## Author

Project built as part of the BAC2 SR curriculum.
