import customtkinter as tk


def afficher_menu():
    frame_connexion.pack_forget()  # cache
    frame_menu.pack()              # affiche

tk.Button(root, text="Connexion", command=afficher_menu)