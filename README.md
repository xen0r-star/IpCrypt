<div align="center">

<img src="images/menuIpCrypt.png" alt="IpCrypt logo" width="320"/>

# IpCrypt

Desktop network tool — Python + CustomTkinter.  
IP verification, subnet analysis, cross-network association, CIDR table, user management.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-2CA5E0?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Phase%201-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-Academic-lightgrey?style=for-the-badge)

</div>

<p align="center">
  <a href="#demo">Demo</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#modules">Modules</a>
</p>

---

## 🎬 Demo

> ⚠️ À venir — ajoute ton GIF ici

<p align="center">
  <img src="images/demo.gif" alt="Application demo" width="700"/>
</p>

---

## 🖼️ Screenshots

### 🔐 Login
<p align="center">
  <img src="images/login.png" width="600"/>
</p>

### 📝 Register (Admin)
<p align="center">
  <img src="images/register.png" width="600"/>
</p>

### 🧭 Menu principal
<p align="center">
  <img src="images/menu.png" width="600"/>
</p>

### 🌐 IP Verification
<p align="center">
  <img src="images/ip_verification.png" width="600"/>
</p>

### 🔗 IP Association
<p align="center">
  <img src="images/ip_association.png" width="600"/>
</p>

### 📊 CIDR Table
<p align="center">
  <img src="images/cidr_table.png" width="600"/>
</p>

---

## 📚 Table of Contents

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

## 🧠 About

IpCrypt is a Python desktop application built for the BAC2 Systems & Networks curriculum.

It provides a GUI-first approach to common IP addressing tasks:
- Class detection
- Subnet calculation
- Cross-network visibility
- CIDR table generation  

⚠️ All calculations are implemented **manually** (no `ipaddress`, `socket`, etc.)

User access is controlled via authentication (admin / client), with credentials stored securely in a MySQL database.

---

## 🚀 Features

| Module | Status | Description |
|---|---|---|
| Splash screen | Done | Animated loading screen |
| Login | Done | Secure authentication |
| Registration | Done | Admin-only user creation |
| Menu | Done | Role-based navigation |
| IP Verification | In progress | Full subnet analysis |
| IP Association | Done | Network comparison |
| CIDR Table | Done | CIDR matrix + Excel export |

---

## 🏗️ Architecture

The app uses a **sequential window model**:
- Each screen is independent (`CTk`)
- No threading
- Clean navigation flow

### Navigation flow

```mermaid
flowchart LR
    A([main.py]) --> B[Splash]
    B --> C[login_screen]

    C -->|login success| D[menu_screen]
    D -->|logout| C

    D -->|IP Verification| F[subnet_inspector]
    D -->|IP Association| G[network_comparator]
    D -->|CIDR Table| H[cidr_explorer]
    D -->|admin only| E[register_screen]

    F --> D
    G --> D
    H --> D
    E --> D
```

---

## 📁 Project Structure

```text
IpCrypt/
├── main.py
├── screens/
├── utils/
├── database/
├── images/
└── requirements.txt
```

---

## 🧰 Tech Stack

- Python 3.10+
- CustomTkinter
- Pillow
- pandas + xlsxwriter
- argon2-cffi
- pymysql

---

## ⚡ Quick Start

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

### 3. Install

```bash
pip install -r requirements.txt
```

### 4. Database

```bash
mysql -u root -p < database/connection.sql
```

### 5. Run

```bash
python main.py
```

---

## 🧩 Modules

### 🔐 Login
- Username + password
- Validation + policy enforcement
- Redirect to menu

### 📝 Registration
- Admin only
- User creation + hashing

### 🧭 Menu
- Role-based UI
- Navigation hub

### 🌐 IP Verification
- Class detection
- Broadcast / host range
- (logic en cours)

### 🔗 IP Association
- Compare 2 réseaux
- Vérification bidirectionnelle

### 📊 CIDR Table
- /8 → /30
- Export Excel

---

## 🔒 Password Policy

| Rule | Value |
|---|---|
| Length | 12+ |
| Uppercase | 2 |
| Digits | 1 |
| Special chars | 1 |

---

## 🛣️ Roadmap

- [ ] Finaliser IP Verification
- [ ] Validation complète des inputs
- [ ] Centraliser UI constants
- [ ] Ajouter `.env` pour DB
- [ ] Tests unitaires
- [ ] Sécurité backend admin

---

## 📸 Images (IMPORTANT)

Ton chemin local :
C:\Users\Corentin\Desktop\BAC2\5.SR\Projet-Phase1\code\images

➡️ Sur GitHub utilise uniquement :
images/nom_image.png

Structure recommandée :
images/
├── login.png
├── register.png
├── menu.png
├── ip_verification.png
├── ip_association.png
├── cidr_table.png
├── demo.gif

---

## 👨‍💻 Author

Projet réalisé dans le cadre du BAC2 Systèmes & Réseaux — Phase 1.
