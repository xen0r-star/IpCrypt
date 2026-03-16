import tkinter as tk
from tkinter import ttk

connexionWindow = tk.Tk() #creation d'une instance de la classe Tk qui représente la fenêtre principale de l'application

connexionWindow.title("Connexion") #titre de la fenêtre

#taille de la fenêtre
window_width = 300
window_height = 200

# get the screen dimension
screen_width = connexionWindow.winfo_screenwidth()
screen_height = connexionWindow.winfo_screenheight()

# find the center point
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

connexionWindow.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

connexionWindow.resizable(False, False) #empêche la redimension de la fenêtre
connexionWindow.iconbitmap("./Python-Emblem.ico") #ajoute une icône à la fenêtre (assurez-vous que le chemin de l'icône est correct)

#connexionWindow.geometry("400x300+50+50") #taille de la fenêtre (largeur x hauteur

#place a label on the connexionWindow
label = tk.Label(connexionWindow, text="welcome to the connexion page").pack() #permet d'afficher le label dans la fenêtre

tk.Label(connexionWindow, text='Classic Label').pack()
ttk.Label(connexionWindow, text='Themed Label').pack()

submit = ttk.Button(connexionWindow, text="Submit").pack() #permet d'afficher un bouton dans la fenêtre


connexionWindow.mainloop() #permet l'affichage en continu de la fenetre