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
  <a href="#modules">Modules</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## Demo

<p align="center">
  <img src="images/demo.gif" alt="Application demo" width="700"/>
</p>

---

## Screenshots

### Login
<p align="center">
  <img src="images/login.png" width="600"/>
</p>

### Register (Admin)
<p align="center">
  <img src="images/register.png" width="600"/>
</p>

### Menu
<p align="center">
  <img src="images/menu.png" width="600"/>
</p>

### IP Verification
<p align="center">
  <img src="images/ip_verification.png" width="600"/>
</p>

### IP Association
<p align="center">
  <img src="images/ip_association.png" width="600"/>
</p>

### CIDR Table
<p align="center">
  <img src="images/cidr_table.png" width="600"/>
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
It provides a GUI-first approach to common IP addressing tasks without relying on networking libraries.

---

## Features

| Module | Status | Description |
|---|---|---|
| Splash screen | Done | Animated loading screen |
| Login | Done | Authentication |
| Registration | Done | Admin user creation |
| Menu | Done | Role-based navigation |
| IP Verification | In progress | Subnet analysis |
| IP Association | Done | Network comparison |
| CIDR Table | Done | CIDR matrix export |

---

## Architecture

Sequential window model using CustomTkinter.

---

## Project Structure

IpCrypt/
├── main.py
├── screens/
├── utils/
├── database/
├── images/
└── requirements.txt

---

## Tech Stack

- Python 3.10+
- CustomTkinter
- Pillow
- pandas + xlsxwriter
- argon2-cffi
- pymysql

---

## Quick Start

git clone <repo-url>
cd IpCrypt

python -m venv .venv

pip install -r requirements.txt

python main.py

---

## Modules

Login, Registration, Menu, IP Verification, IP Association, CIDR Table

---

## Password Policy

| Rule | Value |
|---|---|
| Length | 12+ |
| Uppercase | 2 |
| Digits | 1 |
| Special chars | 1 |

---

## Roadmap

- Complete IP Verification
- Add validation
- Add tests

---

## Author

BAC2 Systems & Networks project.
